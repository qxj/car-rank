# - Try to find the Google Glog library
#
# This module defines the following variables
#
# GLOG_FOUND - Was Glog found
# GLOG_INCLUDE_DIRS - the Glog include directories
# GLOG_LIBRARIES - Link to this
#
# This module accepts the following variables
#
# GLOG_ROOT - Can be set to Glog install path or Windows build path
#

if (NOT DEFINED GLOG_ROOT)
  set (GLOG_ROOT /usr /usr/local)
endif (NOT DEFINED GLOG_ROOT)

set (LIB_PATHS ${GLOG_ROOT} ${GLOG_ROOT}/lib)

# find include
find_path(GLOG_INCLUDE_DIR
  NAMES
  logging.h
  raw_logging.h
  PATHS
  ${GLOG_ROOT}/include/glog
  /usr/include/glog
  )

# find library
find_library(GLOG_LIBRARY
  NAMES
  libglog
  HINTS
  ${GLOG_ROOT}
  PATH_SUFFIXES
  lib64
  lib)

# handle the QUIETLY and REQUIRED arguments and set GLOG_FOUND to TRUE if
# all listed variables are TRUE
include(FindPackageHandleStandardArgs)
find_package_handle_standard_args(Glog
  DEFAULT_MSG
  GLOG_LIBRARY GLOG_INCLUDE_DIR)


if(GLOG_FOUND)
  message(STATUS "glog library found at ${GLOG_LIBRARIES}")

  set(GLOG_INCLUDE_DIRS ${GLOG_INCLUDE_DIR})
  set(GLOG_LIBRARIES ${GLOG_LIBRARY})

  string(REGEX REPLACE "/libglog.so" "" GLOG_LIBRARIES_DIR ${GLOG_LIBRARIES})

  mark_as_advanced(GLOG_LIBRARIES GLOG_INCLUDE_DIRS)

endif()
