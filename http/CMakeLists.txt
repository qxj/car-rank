include_directories(${GLOG_INCLUDE_DIRS} ${GFlags_INCLUDE_DIRS})

aux_source_directory(. HTTP_SRCS)

list(REMOVE_ITEM HTTP_SRCS example_dummy_server.cpp)

add_library(http ${HTTP_SRCS})

add_executable(example_dummy_server example_dummy_server.cpp)

target_link_libraries(example_dummy_server
  http
  ${Boost_LIBRARIES}
  ${GLOG_LIBRARIES}
  ${GFLAGS_LIBRARIES}
  )
