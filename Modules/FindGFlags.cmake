# - Try to find GFlags
#
# The following variables are optionally searched for defaults
# GFLAGS_ROOT_DIR: Base directory where all GFlags components are found
#
# - Try to find GFlags
#
#
# The following are set after configuration is done:
# GFLAGS_FOUND
# GFLAGS_INCLUDE_DIRS
# GFLAGS_LIBRARIES
# GFLAGS_LIBRARY_DIRS

# We are testing only a couple of files in the include directories
find_path(GFLAGS_INCLUDE_DIR
  gflags/gflags.h
  HINTS
  /opt/local/include
  /usr/local/include
  /usr/include
  ${GFLAGS_ROOT_DIR}/src
  )

find_library(GFLAGS_LIBRARY
  NAMES gflags
  HINTS
  /usr
  /usr/local
  PATH_SUFFIXES
  x86_64-linux-gnu
  i386-linux-gnu
  lib64
  lib)

include(FindPackageHandleStandardArgs)
find_package_handle_standard_args(gflags
  DEFAULT_MSG
  GFLAGS_INCLUDE_DIR GFLAGS_LIBRARY)

if (GFLAGS_FOUND)
  set(GFLAGS_LIBRARIES ${GFLAGS_LIBRARY})
  set(GFLAGS_INCLUDE_DIRS ${GFLAGS_INCLUDE_DIR})

  string(REGEX REPLACE "/libgflags.so" "" GFLAGS_LIBRARY_DIRS ${GFLAGS_LIBRARIES})

  include_directories(${GFLAGS_INCLUDE_DIR})
  link_directories(${GFLAGS_LIBRARY_DIR})

  mark_as_advanced(GFLAGS_LIBRARIES GFLAGS_INCLUDE_DIRS)
endif()
