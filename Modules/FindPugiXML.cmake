find_path(PUGIXML_INCLUDE_DIR
  pugixml.hpp
  HINTS
  /opt/local/include
  /usr/local/include
  /usr/include
  )

find_library(PUGIXML_LIBRARY
  NAMES pugixml
  HINTS
  /usr
  /usr/local
  PATH_SUFFIXES
  x86_64-linux-gnu
  i386-linux-gnu
  lib64
  lib)

include(FindPackageHandleStandardArgs)
find_package_handle_standard_args(pugixml
  DEFAULT_MSG
  PUGIXML_INCLUDE_DIR PUGIXML_LIBRARY)

if (PUGIXML_FOUND)
  set(PUGIXML_LIBRARIES ${PUGIXML_LIBRARY})
  set(PUGIXML_INCLUDE_DIRS ${PUGIXML_INCLUDE_DIR})

  string(REGEX REPLACE "/libpugixml.so" "" PUGIXML_LIBRARY_DIRS ${PUGIXML_LIBRARIES})

  include_directories(${PUGIXML_INCLUDE_DIR})
  link_directories(${PUGIXML_LIBRARY_DIR})

  mark_as_advanced(PUGIXML_LIBRARIES PUGIXML_INCLUDE_DIRS)
endif()
