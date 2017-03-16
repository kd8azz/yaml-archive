#ifndef BOOST_ARCHIVE_YAML_ARCHIVE_EXCEPTION_HPP
#define BOOST_ARCHIVE_YAML_ARCHIVE_EXCEPTION_HPP

// MS compatible compilers support #pragma once
#if defined(_MSC_VER)
#pragma once
#endif

/////////1/////////2/////////3/////////4/////////5/////////6/////////7/////////8
// yaml_archive_exception.hpp:

// (C) Copyright 2007 Robert Ramey - http://www.rrsd.com .
// Use, modification and distribution is subject to the Boost Software
// License, Version 1.0. (See accompanying file LICENSE_1_0.txt or copy at
// http://www.boost.org/LICENSE_1_0.txt)

//  See http://www.boost.org for updates, documentation, and revision history.

#include <boost/assert.hpp>
#include <exception>

#include <boost/archive/archive_exception.hpp>
#include <boost/archive/detail/decl.hpp>
#include <boost/config.hpp>

#include <boost/archive/detail/abi_prefix.hpp> // must be the last header

namespace boost {
namespace archive {

//////////////////////////////////////////////////////////////////////
// exceptions thrown by yaml archives
//
class BOOST_SYMBOL_VISIBLE yaml_archive_exception
    : public virtual boost::archive::archive_exception
{
  public:
    typedef enum {
        yaml_archive_parsing_error, // see save_register
        yaml_archive_tag_mismatch,
        yaml_archive_tag_name_error
    } exception_code;
    BOOST_SYMBOL_VISIBLE yaml_archive_exception(exception_code c,
                                                const char*    e1 = NULL,
                                                const char*    e2 = NULL);
    BOOST_SYMBOL_VISIBLE yaml_archive_exception(yaml_archive_exception const&);
    virtual BOOST_SYMBOL_VISIBLE ~yaml_archive_exception()
        BOOST_NOEXCEPT_OR_NOTHROW;
};

} // namespace archive
} // namespace boost

#include <boost/archive/detail/abi_suffix.hpp> // pops abi_suffix.hpp pragmas

#endif // BOOST_YAML_ARCHIVE_ARCHIVE_EXCEPTION_HPP
