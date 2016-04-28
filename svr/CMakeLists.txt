add_executable(ranksvr main.cpp )

include_directories(${PROJECT_SOURCE_DIR}/http)

target_link_libraries(ranksvr
  http
  glog
  gflags
  boost_system
  boost_thread
  pthread)
