# - Try to find Mysql-Connector-C++
# Once done, this will define
#
#  LIBMEMCACHED_FOUND - system has Mysql-Connector-C++ installed
#  LIBMEMCACHED_INCLUDE_DIRS - the Mysql-Connector-C++ include directories
#  LIBMEMCACHED_LIBRARIES - link these to use Mysql-Connector-C++
#
# The user may wish to set, in the CMake GUI or otherwise, this variable:
#  LIBMEMCACHED_ROOT_DIR - path to start searching for the module

set(LIBMEMCACHED_ROOT_DIR
  "${LIBMEMCACHED_ROOT_DIR}"
  CACHE
  PATH
  "Where to start looking for this component.")


find_path(LIBMEMCACHED_INCLUDE_DIR
  memcached.h
  HINTS
  ${LIBMEMCACHED_ROOT_DIR}
  PATH_SUFFIXES
  include)

find_library(LIBMEMCACHED_LIBRARY
  NAMES
  libmemcached
  HINTS
  ${LIBMEMCACHED_ROOT_DIR}
  PATH_SUFFIXES
  lib64
  lib)

# mark_as_advanced(LIBMEMCACHED_INCLUDE_DIR
#   LIBMEMCACHED_LIBRARY)

include(FindPackageHandleStandardArgs)
find_package_handle_standard_args(Libmemcached
  DEFAULT_MSG
  LIBMEMCACHED_INCLUDE_DIR
  LIBMEMCACHED_LIBRARY)

if(LIBMEMCACHED_FOUND)
  set(LIBMEMCACHED_INCLUDE_DIRS "${LIBMEMCACHED_INCLUDE_DIR}")
  set(LIBMEMCACHED_LIBRARIES "${LIBMEMCACHED_LIBRARY}")

  include_directories(${LIBMEMCACHED_INCLUDE_DIRS})
  link_libraries(${LIBMEMCACHED_LIBRARIES})

  mark_as_advanced(LIBMEMCACHED_INCLUDE_DIRS
    LIBMEMCACHED_LIBRARIES)
  # mark_as_advanced(LIBMEMCACHED_ROOT_DIR)
endif()
