# - Try to find Mysql-Connector-C++
# Once done, this will define
#
#  MEMCACHED_FOUND - system has Mysql-Connector-C++ installed
#  MEMCACHED_INCLUDE_DIRS - the Mysql-Connector-C++ include directories
#  MEMCACHED_LIBRARIES - link these to use Mysql-Connector-C++
#
# The user may wish to set, in the CMake GUI or otherwise, this variable:
#  MEMCACHED_ROOT_DIR - path to start searching for the module

set(MEMCACHED_ROOT_DIR
  "${MEMCACHED_ROOT_DIR}"
  CACHE
  PATH
  "Where to start looking for this component.")


find_path(MEMCACHED_INCLUDE_DIR
  memcached.h
  HINTS
  ${MEMCACHED_ROOT_DIR}
  PATH_SUFFIXES
  include)

find_library(MEMCACHED_LIBRARY
  NAMES
  libmemcached
  HINTS
  ${MEMCACHED_ROOT_DIR}
  PATH_SUFFIXES
  lib64
  lib)

# mark_as_advanced(MEMCACHED_INCLUDE_DIR
#   MEMCACHED_LIBRARY)

include(FindPackageHandleStandardArgs)
find_package_handle_standard_args(Memcached
  DEFAULT_MSG
  MEMCACHED_INCLUDE_DIR
  MEMCACHED_LIBRARY)

if(MEMCACHED_FOUND)
  set(MEMCACHED_INCLUDE_DIRS "${MEMCACHED_INCLUDE_DIR}")
  set(MEMCACHED_LIBRARIES "${MEMCACHED_LIBRARY}")

  include_directories(${MEMCACHED_INCLUDE_DIRS})
  link_libraries(${MEMCACHED_LIBRARIES})

  mark_as_advanced(MEMCACHED_INCLUDE_DIRS
    MEMCACHED_LIBRARIES)
  # mark_as_advanced(MEMCACHED_ROOT_DIR)
endif()
