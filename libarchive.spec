Name:           libarchive
Version:        2.8.3
Release:        7%{?dist}
Summary:        A library for handling streaming archive formats 

Group:          System Environment/Libraries
License:        BSD
URL:            http://code.google.com/p/libarchive/
Source0:        http://libarchive.googlecode.com/files/libarchive-%{version}.tar.gz
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)


BuildRequires: autoconf, automake, bison, libtool
BuildRequires: sharutils
BuildRequires: zlib-devel
BuildRequires: bzip2-devel
BuildRequires: xz-devel
BuildRequires: e2fsprogs-devel
BuildRequires: libacl-devel
BuildRequires: libattr-devel
BuildRequires: openssl-devel
BuildRequires: libxml2-devel


# from upstream
# https://bugzilla.redhat.com/show_bug.cgi?id=597243
Patch0: libarchive-2.8.4-iso9660-data-types.patch
# CVE-2010-4666 CVE-2011-1777 CVE-2011-1778 CVE-2011-1779 libarchive: multiple vulnerabilities in version 2.8.4
# https://bugzilla.redhat.com/show_bug.cgi?id=739940
Patch1: CVE-2011-1777.patch
Patch2: CVE-2011-1778.patch

# Patch needed to make the testsuite at least "somehow" work.  This is done with
# intention that we would see potential breakage in the following set of CVE
# patches.  Particular notes follow.
# * test_read_format_isorr_rr_moved: Broken due to CVE-2011-1777 fix.  I don't
# have mandate to work on this atm.
# * test_write_disk, test_write_disk_times, test_read_format_tz: I don't know
# why those fail in brew.  On my box (in epel6 mock) and within internal Copr
# (rhel/centos mocks) those test cases pass, so most probably some environment
# issue.
Patch3: libarchive-2.8.3-testsuite.patch

# Set of summer 2016 CVE patches.
Patch4: libarchive-2.8.3-rhbz-1347086.patch
Patch5: libarchive-2.8.3-CVE-2015-8920.patch
Patch6: libarchive-2.8.3-CVE-2015-8921.patch
Patch7: libarchive-2.8.3-CVE-2015-8932.patch
Patch8: libarchive-2.8.3-CVE-2016-4809.patch
Patch9: libarchive-2.8.3-CVE-2016-5844.patch

Patch10: libarchive-2.8.3-CVE-2016-5418.patch
Patch11: libarchive-2.8.3-CVE-2016-5418-variation.patch


%description
Libarchive is a programming library that can create and read several different 
streaming archive formats, including most popular tar variants, several cpio 
formats, and both BSD and GNU ar variants. It can also write shar archives and 
read ISO9660 CDROM images and ZIP archives.

%package        devel
Summary:        Development files for %{name}
Group:          Development/Libraries
Requires:       %{name} = %{version}-%{release}

%description    devel
The %{name}-devel package contains libraries and header files for
developing applications that use %{name}.


%prep
%setup -q
%patch0 -p0 -b .iso9660-testsuite
%patch1 -p1 -b .CVE-2011-1777
%patch2 -p1 -b .CVE-2011-1778
%patch3 -p1 -b .testsuite
%patch4 -p1 -b .rhbz-1347086
%patch5 -p1 -b .CVE-2015-8920
%patch6 -p1 -b .CVE-2015-8921
%patch7 -p1 -b .CVE-2015-8932
%patch8 -p1 -b .CVE-2016-4809
%patch9 -p1 -b .CVE-2016-5844
%patch10 -p1 -b .CVE-2016-5418
%patch11 -p1 -b .CVE-2016-5418-var
autoreconf -vi


%build
%configure --disable-static --disable-bsdtar --disable-bsdcpio
make %{?_smp_mflags}


%install
rm -rf $RPM_BUILD_ROOT
make install DESTDIR=$RPM_BUILD_ROOT
iconv -f latin1 -t utf-8 < NEWS > NEWS.utf8; cp NEWS.utf8 NEWS
find $RPM_BUILD_ROOT -name '*.la' -exec rm -f {} ';'
find $RPM_BUILD_ROOT -name cpio.5 -exec rm -f {} ';'
find $RPM_BUILD_ROOT -name mtree.5 -exec rm -f {} ';'
find $RPM_BUILD_ROOT -name tar.5 -exec rm -f {} ';'


%check
make libarchive_test %{?_smp_mflags}
./libarchive_test -vvv -d


%clean
rm -rf $RPM_BUILD_ROOT


%post -p /sbin/ldconfig

%postun -p /sbin/ldconfig


%files
%defattr(-,root,root,-)
%doc COPYING README NEWS
%{_libdir}/*.so.*


%files devel
%defattr(-,root,root,-)
%doc
%{_includedir}/*
%{_mandir}/*/*
%{_libdir}/*.so
%{_libdir}/pkgconfig/*


%changelog
* Fri Aug 12 2016 Petr Kubat <pkubat@redhat.com> - 2.8.3-7
- Fixes variation of CVE-2016-5418: Hard links could include ".." in their path.

* Thu Aug 11 2016 Petr Kubat <pkubat@redhat.com> - 2.8.3-6
- Fixes CVE-2016-5418: Archive Entry with type 1 (hardlink) causes file overwrite (#1365774)

* Mon Jul 18 2016 Pavel Raiskup <praiskup@redhat.com> - 2.8.3-5
- enable testsuite
- CVE batch in summer 2016

* Fri Feb  3 2012 Tomas Bzatek <tbzatek@redhat.com> - 2.8.3-4
- Updated CVE-2011-1777 fix (#783375)

* Mon Oct  3 2011 Tomas Bzatek <tbzatek@redhat.com> - 2.8.3-3
- Security fixes (CVE-2011-1777, CVE-2011-1778) (#739940)

* Fri Jun 25 2010 Tomas Bzatek <tbzatek@redhat.com> - 2.8.3-2
- Fix ISO9660 reader data type mismatches (#597243)

* Wed May 26 2010 Tomas Bzatek <tbzatek@redhat.com> - 2.8.3-1
- Update to 2.8.3

* Mon May 17 2010 Tomas Bzatek <tbzatek@redhat.com> - 2.8.0-2
- Cleanup for package review

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

* Wed Mar 18 2008 Tomas Bzatek <tbzatek@redhat.com> 2.4.14-1
- Initial packaging
