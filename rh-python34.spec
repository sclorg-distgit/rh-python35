%global scl_name_prefix rh-
%global scl_name_base python
%global scl_name_version 35
%global scl %{scl_name_prefix}%{scl_name_base}%{scl_name_version}

## General notes about python33 SCL packaging
# - the names of packages are NOT prefixed with 'python3-' (e.g. are the same as in Fedora)
# - the names of binaries of Python 3 itself are both python{-debug,...} and python3{-debug,...}
#   so both are usable in shebangs, the non-versioned binaries are preferred.
# - the names of other binaries are NOT prefixed with 'python3-'.
# - there are both macros in '3' variant and non-versioned variant, e.g. both %%{__python}
#   and %%{__python3} are available

%global nfsmountable 1

%scl_package %scl
%global _turn_off_bytecompile 1

%global install_scl 1

# do not produce empty debuginfo package
%global debug_package %{nil}

Summary: Package that installs %scl
Name: %scl_name
Version: 2.0
Release: 1%{?dist}
License: GPLv2+
Source0: macros.additional.%{scl}
Source1: README
Source2: LICENSE
Source3: pythondeps-scl-35.sh
Source4: pkgconfigdeps-scl-35.sh
BuildRequires: help2man
# workaround for https://bugzilla.redhat.com/show_bug.cgi?id=857354
BuildRequires: iso-codes
BuildRequires: scl-utils-build
%if 0%{?install_scl}
Requires: %{scl_prefix}python
%endif

%description
This is the main package for %scl Software Collection.

%package runtime
Summary: Package that handles %scl Software Collection.
Requires: scl-utils

%description runtime
Package shipping essential scripts to work with %scl Software Collection.

%package build
Summary: Package shipping basic build configuration
Requires: scl-utils-build

%description build
Package shipping essential configuration macros to build %scl Software Collection.

%package scldevel
Summary: Package shipping development files for %scl

%description scldevel
Package shipping development files, especially usefull for development of
packages depending on %scl Software Collection.

%prep
%setup -T -c

# This section generates README file from a template and creates man page
# from that file, expanding RPM macros in the template file.
cat >README <<'EOF'
%{expand:%(cat %{SOURCE1})}
EOF

# copy the license file so %%files section sees it
cp %{SOURCE2} .

%build
# generate a helper script that will be used by help2man
cat >h2m_helper <<'EOF'
#!/bin/bash
[ "$1" == "--version" ] && echo "%{scl_name} %{version} Software Collection" || cat README
EOF
chmod a+x h2m_helper

# generate the man page
help2man -N --section 7 ./h2m_helper -o %{scl_name}.7

%install
%scl_install

cat >> %{buildroot}%{_scl_scripts}/enable << EOF
export PATH=%{_bindir}\${PATH:+:\${PATH}}
export LD_LIBRARY_PATH=%{_libdir}\${LD_LIBRARY_PATH:+:\${LD_LIBRARY_PATH}}
export MANPATH=%{_mandir}:\$MANPATH
export PKG_CONFIG_PATH=%{_libdir}/pkgconfig\${PKG_CONFIG_PATH:+:\${PKG_CONFIG_PATH}}
# For SystemTap.
export XDG_DATA_DIRS=%{_datadir}\${XDG_DATA_DIRS:+:\${XDG_DATA_DIRS}}
EOF

# Add the aditional macros to macros.%%{scl}-config
cat %{SOURCE0} >> %{buildroot}%{_root_sysconfdir}/rpm/macros.%{scl}-config
# instead of replacing @scl@ with %{scl} macro we replace it with scl_name_base and scl_name_version
# because scl macro contains vendor prefix rh- and this leads to wrong macro names 
# (macro can't contain -) and erros like %rh has illegal name
sed -i 's|@scl@|%{scl_name_base}%{scl_name_version}|g' %{buildroot}%{_root_sysconfdir}/rpm/macros.%{scl}-config
sed -i 's|@vendorscl@|%{scl}|g' %{buildroot}%{_root_sysconfdir}/rpm/macros.%{scl}-config

# Create the scldevel subpackage macros
cat >> %{buildroot}%{_root_sysconfdir}/rpm/macros.%{scl_name_base}-scldevel << EOF
%%scl_%{scl_name_base} %{scl}
%%scl_prefix_%{scl_name_base} %{scl_prefix}
EOF

mkdir -p %{buildroot}%{_root_prefix}/lib/rpm
cp -a %{SOURCE3} %{buildroot}%{_root_prefix}/lib/rpm
cp -a %{SOURCE4} %{buildroot}%{_root_prefix}/lib/rpm

# install generated man page
mkdir -p %{buildroot}%{_mandir}/man7/
install -m 644 %{scl_name}.7 %{buildroot}%{_mandir}/man7/%{scl_name}.7

%files

%files runtime -f filelist
%doc README LICENSE
%scl_files
%{_mandir}/man7/%{scl_name}.*

%files build
%{_root_sysconfdir}/rpm/macros.%{scl}-config
%{_root_prefix}/lib/rpm/pythondeps-scl-35.sh
%{_root_prefix}/lib/rpm/pkgconfigdeps-scl-35.sh

%files scldevel
%{_root_sysconfdir}/rpm/macros.%{scl_name_base}-scldevel

%changelog
* Tue Nov 24 2015 Robert Kuska <rkuska@redhat.com> - 2.0-1
- Create python35 metapackage
