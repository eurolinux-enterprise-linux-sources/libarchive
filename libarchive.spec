Name:           libarchive
Version:        3.1.2
Release:        5%{?dist}
Summary:        A library for handling streaming archive formats

Group:          System Environment/Libraries
License:        BSD
URL:            http://www.libarchive.org/
Source0:        http://www.libarchive.org/downloads/%{name}-%{version}.tar.gz
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)


BuildRequires: bison
BuildRequires: sharutils
BuildRequires: zlib-devel
BuildRequires: bzip2-devel
BuildRequires: xz-devel
BuildRequires: lzo-devel
BuildRequires: e2fsprogs-devel
BuildRequires: libacl-devel
BuildRequires: libattr-devel
BuildRequires: openssl-devel
BuildRequires: libxml2-devel
BuildRequires: automake autoconf libtool


# CVE-2013-0211 libarchive: read buffer overflow on 64-bit systems
# https://bugzilla.redhat.com/show_bug.cgi?id=927105
Patch0: libarchive-3.1.3-CVE-2013-0211_read_buffer_overflow.patch

Patch1: libarchive-3.1.2-testsuite.patch

%description
Libarchive is a programming library that can create and read several different
streaming archive formats, including most popular tar variants, several cpio
formats, and both BSD and GNU ar variants. It can also write shar archives and
read ISO9660 CDROM images and ZIP archives.

%package        devel
Summary:        Development files for %{name}
Group:          Development/Libraries
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description    devel
The %{name}-devel package contains libraries and header files for
developing applications that use %{name}.


%package -n     bsdtar
Summary:        Manipulate tape archives
Group:          Applications/File
Requires:       %{name} = %{version}-%{release}

%description -n bsdtar
The bsdtar package contains standalone bsdtar utility split off regular
libarchive packages.


%package -n     bsdcpio
Summary:        Copy files to and from archives
Group:          Applications/File
Requires:       %{name} = %{version}-%{release}

%description -n bsdcpio
The bsdcpio package contains standalone bsdcpio utility split off regular
libarchive packages.


%prep
%setup -q -n %{name}-%{version}
%patch0 -p1 -b .CVE-2013-0211
# fix bugs in testsuite
# ~> upstream ~> 26629c191a & b539b2e597 & 9caa49246
%patch1 -p1 -b .fix-testsuite


%build
build/autogen.sh
%configure --disable-static --disable-rpath
# remove rpaths
sed -i 's|^hardcode_libdir_flag_spec=.*|hardcode_libdir_flag_spec=""|g' libtool
sed -i 's|^runpath_var=LD_RUN_PATH|runpath_var=DIE_RPATH_DIE|g' libtool

test -z "$V" && verbose_make="V=1"
make %{?_smp_mflags} $verbose_make


%install
rm -rf $RPM_BUILD_ROOT
make install DESTDIR=$RPM_BUILD_ROOT
find $RPM_BUILD_ROOT -name '*.la' -exec rm -f {} ';'


%check
run_testsuite()
{
    LD_LIBRARY_PATH=`pwd`/.libs make check -j1
    res=$?
    echo $res
    if [ $res -ne 0 ]; then
        # error happened - try to extract in koji as much info as possible
        cat test-suite.log
        echo "========================="
        err=`cat test-suite.log | grep "Details for failing tests" | cut -d: -f2`
        for i in $err; do
            find $i -printf "%p\n    ~> a: %a\n    ~> c: %c\n    ~> t: %t\n    ~> %s B\n"
            echo "-------------------------"
            cat $i/*.log
        done
        return 1
    else
        return 0
    fi
}

# On a ppc/ppc64 is some race condition causing 'make check' fail on ppc
# when both 32 and 64 builds are done in parallel on the same machine in
# koji.  Try to run once again if failed.
%ifarch ppc
run_testsuite || run_testsuite
%else
run_testsuite
%endif


%clean
rm -rf $RPM_BUILD_ROOT


%post -p /sbin/ldconfig


%postun -p /sbin/ldconfig


%files
%defattr(-,root,root,-)
%doc COPYING README NEWS
%{_libdir}/libarchive.so.13*
%{_mandir}/*/cpio.*
%{_mandir}/*/mtree.*
%{_mandir}/*/tar.*

%files devel
%defattr(-,root,root,-)
%doc
%{_includedir}/*.h
%{_mandir}/*/archive*
%{_mandir}/*/libarchive*
%{_libdir}/libarchive.so
%{_libdir}/pkgconfig/libarchive.pc

%files -n bsdtar
%defattr(-,root,root,-)
%doc COPYING README NEWS
%{_bindir}/bsdtar
%{_mandir}/*/bsdtar*

%files -n bsdcpio
%defattr(-,root,root,-)
%doc COPYING README NEWS
%{_bindir}/bsdcpio
%{_mandir}/*/bsdcpio*


%changelog
* Mon Jul 22 2013 Pavel Raiskup <praiskup@redhat.com> - 3.1.2-5
- try to workaround racy testsuite fail

* Sun Jun 30 2013 Pavel Raiskup <praiskup@redhat.com> - 3.1.2-4
- enable testsuite in the %%check phase

* Mon Jun 24 2013 Pavel Raiskup <praiskup@redhat.com> - 3.1.2-3
- bsdtar/bsdcpio should require versioned libarchive

* Wed Apr  3 2013 Tomas Bzatek <tbzatek@redhat.com> - 3.1.2-2
- Remove libunistring-devel build require

* Thu Mar 28 2013 Tomas Bzatek <tbzatek@redhat.com> - 3.1.2-1
- Update to 3.1.2
- Fix CVE-2013-0211: read buffer overflow on 64-bit systems (#927105)

* Thu Feb 14 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 3.1.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_19_Mass_Rebuild

* Mon Jan 14 2013 Tomas Bzatek <tbzatek@redhat.com> - 3.1.1-1
- Update to 3.1.1
- NEWS seems to be valid UTF-8 nowadays

* Wed Oct 03 2012 Pavel Raiskup <praiskup@redhat.com> - 3.0.4-3
- better install manual pages for libarchive/bsdtar/bsdcpio (# ... )
- several fedora-review fixes ...:
- Source0 has moved to github.com
- remove trailing white spaces
- repair summary to better describe bsdtar/cpiotar utilities

* Thu Jul 19 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 3.0.4-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Mon May  7 2012 Tomas Bzatek <tbzatek@redhat.com> - 3.0.4-1
- Update to 3.0.4

* Wed Feb  1 2012 Tomas Bzatek <tbzatek@redhat.com> - 3.0.3-2
- Enable bsdtar and bsdcpio in separate subpackages (#786400)

* Fri Jan 13 2012 Tomas Bzatek <tbzatek@redhat.com> - 3.0.3-1
- Update to 3.0.3

* Fri Jan 13 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 3.0.0-0.3.a
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Tue Nov 15 2011 Rex Dieter <rdieter@fedoraproject.org> 3.0.0-0.2.a
- track files/sonames closer, so abi bumps aren't a surprise
- tighten subpkg deps via %%_isa

* Mon Nov 14 2011 Tomas Bzatek <tbzatek@redhat.com> - 3.0.0-0.1.a
- Update to 3.0.0a (alpha release)

* Mon Sep  5 2011 Tomas Bzatek <tbzatek@redhat.com> - 2.8.5-1
- Update to 2.8.5

* Mon Feb 07 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.8.4-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Thu Jan 13 2011 Tomas Bzatek <tbzatek@redhat.com> - 2.8.4-2
- Rebuild for new xz-libs

* Wed Jun 30 2010 Tomas Bzatek <tbzatek@redhat.com> - 2.8.4-1
- Update to 2.8.4

* Fri Jun 25 2010 Tomas Bzatek <tbzatek@redhat.com> - 2.8.3-2
- Fix ISO9660 reader data type mismatches (#597243)

* Tue Mar 16 2010 Tomas Bzatek <tbzatek@redhat.com> - 2.8.3-1
- Update to 2.8.3

* Mon Mar  8 2010 Tomas Bzatek <tbzatek@redhat.com> - 2.8.1-1
- Update to 2.8.1

* Fri Feb  5 2010 Tomas Bzatek <tbzatek@redhat.com> - 2.8.0-1
- Update to 2.8.0

* Wed Jan  6 2010 Tomas Bzatek <tbzatek@redhat.com> - 2.7.902a-1
- Update to 2.7.902a

* Fri Aug 21 2009 Tomas Mraz <tmraz@redhat.com> - 2.7.1-2
- rebuilt with new openssl

* Fri Aug  7 2009 Tomas Bzatek <tbzatek@redhat.com> 2.7.1-1
- Update to 2.7.1
- Drop deprecated lzma dependency, libxz handles both formats

* Mon Jul 27 2009 Tomas Bzatek <tbzatek@redhat.com> 2.7.0-3
- Enable XZ compression format

* Fri Jul 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.7.0-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Tue May 12 2009 Tomas Bzatek <tbzatek@redhat.com> 2.7.0-1
- Update to 2.7.0

* Fri Mar  6 2009 Tomas Bzatek <tbzatek@redhat.com> 2.6.2-1
- Update to 2.6.2

* Wed Feb 25 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.6.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Mon Feb 16 2009 Tomas Bzatek <tbzatek@redhat.com> 2.6.1-1
- Update to 2.6.1

* Thu Jan  8 2009 Tomas Bzatek <tbzatek@redhat.com> 2.6.0-1
- Update to 2.6.0

* Mon Dec 15 2008 Tomas Bzatek <tbzatek@redhat.com> 2.5.904a-1
- Update to 2.5.904a

* Tue Dec  9 2008 Tomas Bzatek <tbzatek@redhat.com> 2.5.903a-2
- Add LZMA support

* Mon Dec  8 2008 Tomas Bzatek <tbzatek@redhat.com> 2.5.903a-1
- Update to 2.5.903a

* Tue Jul 22 2008 Tomas Bzatek <tbzatek@redhat.com> 2.5.5-1
- Update to 2.5.5

* Wed Apr  2 2008 Tomas Bzatek <tbzatek@redhat.com> 2.4.17-1
- Update to 2.4.17

* Wed Mar 19 2008 Tomas Bzatek <tbzatek@redhat.com> 2.4.14-1
- Initial packaging
