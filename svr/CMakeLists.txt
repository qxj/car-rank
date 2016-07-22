aux_source_directory(. SVR_SRCS)

add_executable(ranksvr ${SVR_SRCS} )

include_directories(${PROJECT_SOURCE_DIR}/http
  ${PROJECT_SOURCE_DIR}/ranking)

include_directories(${CMAKE_SOURCE_DIR}/thirdparty
  ${CMAKE_SOURCE_DIR}/util)

include_directories(${GLOG_INCLUDE_DIRS}
  ${GFLAGS_INCLUDE_DIRS}
  ${GTEST_INCLUDE_DIRS}
  ${MEMCACHED_INCLUDE_DIRS}
  ${PUGIXML_INCLUDE_DIRS})

target_link_libraries(ranksvr
  util
  http
  ranking
  ${Boost_LIBRARIES}
  ${GLOG_LIBRARIES}
  ${GFLAGS_LIBRARIES}
  ${MYSQLCONNECTORCPP_LIBRARIES}
  ${MEMCACHED_LIBRARIES}
  ${MEMCACHEDUTIL_LIBRARIES}
  ${MYSQL_LIBRARIES}
  ${PUGIXML_LIBRARIES}
  ${ZLIB_LIBRARIES}
  ${CMAKE_DL_LIBS}
  )
