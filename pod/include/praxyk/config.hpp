#ifndef INCLUDED_PRAXYK_CONFIG_HPP
#define INCLUDED_PRAXYK_CONFIG_HPP

/***************************************************************************
 * Allow use of and/or/not
 ***************************************************************************/
#include <ciso646>

/***************************************************************************
 * Define cross-platform macros
 ***************************************************************************/
#if defined(_MSC_VER)
#    define PRAXYK_EXPORT         __declspec(dllexport)
#    define PRAXYK_IMPORT         __declspec(dllimport)
#    define PRAXYK_INLINE         __forceinline
#    define PRAXYK_UNUSED(x)      x
#    pragma warning(disable: 4251) // class 'A<T>' needs to have dll-interface to be used by clients of class 'B'
#elif defined(__GNUG__) && __GNUG__ >= 4
#    define PRAXYK_EXPORT         __attribute__((visibility("default")))
#    define PRAXYK_IMPORT         __attribute__((visibility("default")))
#    define PRAXYK_INLINE         inline __attribute__((always_inline))
#    define PRAXYK_UNUSED(x)      x __attribute__((unused))
#else
#    define PRAXYK_EXPORT
#    define PRAXYK_IMPORT
#    define PRAXYK_INLINE         inline
#    define PRAXYK_UNUSED(x)      x
#endif

#ifdef PRAXYK_DLL_EXPORTS
#    define PRAXYK_API PRAXYK_EXPORT
#else
#    define PRAXYK_API PRAXYK_IMPORT
#endif

#if defined(linux) || defined(__linux) || defined(__linux__)
#    define PRAXYK_PLATFORM_LINUX
#elif defined(__MINGW32__) || defined(MINGW32)
#    define PRAXYK_PLATFORM_MINGW
#elif defined(_WIN32) || defined(__WIN32__) || defined(WIN32)
#    define PRAXYK_PLATFORM_WIN32
#elif defined(macintosh) || defined(__APPLE__) || defined(__APPLE_CC__)
#    define PRAXYK_PLATFORM_MACOS
#endif

#endif /* INCLUDED_PRAXYK_CONFIG_HPP */
