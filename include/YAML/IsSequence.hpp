/**
 * @author Raoul Wols
 *
 * @file   Defines which types are "YAML sequence like".
 */

#pragma once

#include <list>
#include <vector>
// TODO: forward_list doesn't have push_back.

#include <YAML/nsbegin.hpp>

template <class T> struct IsSequence_
{
    static constexpr bool value = false;
};

template <class T> static constexpr bool IsSequence = IsSequence_<T>::value;

template <class T, class Alloc> struct IsSequence_<std::vector<T, Alloc>>
{
    static constexpr bool value = true;
};

template <class T, class Alloc> struct IsSequence_<std::list<T, Alloc>>
{
    static constexpr bool value = true;
};

#include <YAML/nsend.hpp>
