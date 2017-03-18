#ifndef BOOST_ARCHIVE_YAML_OARCHIVE_HPP
#define BOOST_ARCHIVE_YAML_OARCHIVE_HPP

// MS compatible compilers support #pragma once
#if defined(_MSC_VER)
#pragma once
#endif

/////////1/////////2/////////3/////////4/////////5/////////6/////////7/////////8
// yaml_oarchive.hpp

// (C) Copyright 2002 Robert Ramey - http://www.rrsd.com .
// Use, modification and distribution is subject to the Boost Software
// License, Version 1.0. (See accompanying file LICENSE_1_0.txt or copy at
// http://www.boost.org/LICENSE_1_0.txt)

//  See http://www.boost.org for updates, documentation, and revision history.

#include <ostream>

#include <boost/config.hpp>
#include <cstddef> // size_t
#if defined(BOOST_NO_STDC_NAMESPACE)
namespace std {
using ::size_t;
} // namespace std
#endif

#include <boost/archive/basic_text_oprimitive.hpp>
#include <boost/archive/basic_yaml_oarchive.hpp>
#include <boost/archive/detail/auto_link_archive.hpp>
#include <boost/archive/detail/register_archive.hpp>
#include <boost/serialization/item_version_type.hpp>
#if BOOST_VERSION < 105600
#include <boost/archive/shared_ptr_helper.hpp>
#endif

#include <boost/archive/detail/abi_prefix.hpp> // must be the last header

#ifdef BOOST_MSVC
#pragma warning(push)
#pragma warning(disable : 4511 4512)
#endif

namespace boost {
namespace archive {

namespace detail {
template <class Archive> class interface_oarchive;
} // namespace detail

/**
 * @brief      YAML output archive for a narrow character stream.
 *
 * Don't use this class directly. Instead, use boost::archive::yaml_oarchive.
 *
 * @tparam     Archive  The derived archive class.
 */
template <class Archive>
class BOOST_SYMBOL_VISIBLE yaml_oarchive_impl
    : public basic_text_oprimitive<std::ostream>,
      public basic_yaml_oarchive<Archive>
{
#ifdef BOOST_NO_MEMBER_TEMPLATE_FRIENDS
  public:
#else
  protected:
    friend class detail::interface_oarchive<Archive>;
    friend class basic_yaml_oarchive<Archive>;
    friend class save_access;
#endif

    template <class T> void save(const T& t)
    {
        basic_text_oprimitive<std::ostream>::save(t);
    }
    void save(const version_type& t)
    {
        save(static_cast<const unsigned int>(t));
    }
    void save(const boost::serialization::item_version_type& t)
    {
        save(static_cast<const unsigned int>(t));
    }
    YAML_ARCHIVE_API void save(const char* t);
#ifndef BOOST_NO_INTRINSIC_WCHAR_T
    YAML_ARCHIVE_API void save(const wchar_t* t);
#endif
    YAML_ARCHIVE_API void save(const std::string& s);
#ifndef BOOST_NO_STD_WSTRING
    YAML_ARCHIVE_API void save(const std::wstring& ws);
#endif
    YAML_ARCHIVE_API
    yaml_oarchive_impl(std::ostream& os, unsigned int flags);
    YAML_ARCHIVE_API
    ~yaml_oarchive_impl();

  public:
    YAML_ARCHIVE_API
    void save_binary(const void* address, std::size_t count);
};

} // namespace archive
} // namespace boost

#ifdef BOOST_MSVC
#pragma warning(pop)
#endif

#include <boost/archive/detail/abi_suffix.hpp> // pops abi_suffix.hpp pragmas

#ifdef BOOST_MSVC
#pragma warning(push)
#pragma warning(disable : 4511 4512)
#endif

namespace boost {
namespace archive {

/**
 * @brief      Concrete YAML output archive for a narrow character stream.
 *
 * Use this class to output your classes to a YAML archive.
 * Do not derive from this class.  If you want to extend this functionality via
 * inhertance, derive from yaml_oarchive_impl instead. This will preserve
 * correct static polymorphism.
 *
 * @tparam     Archive  The derived archive class.
 */
#if BOOST_VERSION < 105600
class BOOST_SYMBOL_VISIBLE yaml_oarchive
    : public yaml_oarchive_impl<yaml_oarchive>,
      public detail::shared_ptr_helper
{
#else
class BOOST_SYMBOL_VISIBLE yaml_oarchive
    : public yaml_oarchive_impl<yaml_oarchive>
{
#endif
  public:
    /**
     * @brief      Constructor.
     *
     * @param      os     The output stream.
     * @param[in]  flags  The flags.
     *
     * @see boost::archive::yaml_iarchive for its input counter-part.
     * @see http://www.boost.org/doc/libs/1_63_0/boost/archive/basic_archive.hpp
     * for the available flags.
     */
    yaml_oarchive(std::ostream& os, unsigned int flags = 0)
        : yaml_oarchive_impl<yaml_oarchive>(os, flags)
    {
    }
    ~yaml_oarchive() {}
};

} // namespace archive
} // namespace boost

// required by export
BOOST_SERIALIZATION_REGISTER_ARCHIVE(boost::archive::yaml_oarchive)

#ifdef BOOST_MSVC
#pragma warning(pop)
#endif

#endif // BOOST_ARCHIVE_YAML_OARCHIVE_HPP
