#ifndef INCLUDED_PRAXYK_SPAM_HPP
#define INCLUDED_PRAXYK_SPAM_HPP

#include <praxyk/config.hpp>

#include <string>

namespace praxyk {
    PRAXYK_API float get_spam_chance(
        const std::string &message
    );
}

/* INCLUDED_PRAXYK_SPAM_HPP */
