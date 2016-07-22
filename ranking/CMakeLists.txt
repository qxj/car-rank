
include_directories(${CMAKE_SOURCE_DIR}/thirdparty)

include_directories(${GLOG_INCLUDE_DIRS}
  ${GFLAGS_INCLUDE_DIRS}
  ${GTEST_INCLUDE_DIRS}
  ${PUGIXML_INCLUDE_DIRS})

add_definitions(-DRAPIDJSON_HAS_STDSTRING)

aux_source_directory(. RANKING_SRCS)

list(REMOVE_ITEM RANKING_SRCS json_request_test.cpp)
list(REMOVE_ITEM RANKING_SRCS ensemble_test.cpp)

add_library(ranking ${RANKING_SRCS})

# json_request_test
add_executable(json_request_test json_request_test.cpp)

target_link_libraries(json_request_test
  ranking
  ${GLOG_LIBRARIES}
  ${GFLAGS_LIBRARIES}
  ${GTEST_LIBRARY}
  ${GTEST_MAIN_LIBRARY})

add_test(json_request_test json_request_test)

# ensemble_test
add_executable(ensemble_test ensemble_test.cpp)

target_link_libraries(ensemble_test
  ranking
  ${GLOG_LIBRARIES}
  ${GFLAGS_LIBRARIES}
  ${GTEST_LIBRARY}
  ${GTEST_MAIN_LIBRARY}
  ${PUGIXML_LIBRARIES})

add_test(ensemble_test ensemble_test)
