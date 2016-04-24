add_executable(ranksvr main.cpp )

include_directories(${PROJECT_SOURCE_DIR}/http)

include_directories(${GLOG_INCLUDE_DIRS} ${GFlags_INCLUDE_DIRS})

target_link_libraries(ranksvr
  http
  ${Boost_LIBRARIES}
  ${GLOG_LIBRARIES}
  ${GFlags_LIBS}
  )
