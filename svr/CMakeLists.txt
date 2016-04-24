aux_source_directory(. SVR_SRCS)

add_executable(ranksvr ${SVR_SRCS} )

include_directories(${PROJECT_SOURCE_DIR}/http
  ${PROJECT_SOURCE_DIR}/ranking)

include_directories(${CMAKE_SOURCE_DIR}/thirdparty)

include_directories(${GLOG_INCLUDE_DIRS} ${GFLAGS_INCLUDE_DIRS})

target_link_libraries(ranksvr
  http
  ranking
  ${Boost_LIBRARIES}
  ${GLOG_LIBRARIES}
  ${GFLAGS_LIBRARIES}
  ${MYSQLCONNECTORCPP_LIBRARIES}
  mysqlclient_r
  )
