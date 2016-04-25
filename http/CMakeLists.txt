include_directories(${GLOG_INCLUDE_DIRS} ${GFlags_INCLUDE_DIRS})

aux_source_directory(. HTTP_SRCS)

list(REMOVE_ITEM HTTP_SRCS dummy_server.cpp)

add_library(http ${HTTP_SRCS})

add_executable(dummy_server dummy_server.cpp)

target_link_libraries(dummy_server
  http
  ${Boost_LIBRARIES}
  ${GLOG_LIBRARIES}
  ${GFLAGS_LIBRARIES}
  )
