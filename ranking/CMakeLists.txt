# aux_source_directory(. RANKING_SRCS)

# add_library(ranking ${RANKING_SRCS})

include_directories(${CMAKE_SOURCE_DIR}/thirdparty)

include_directories(${GLOG_INCLUDE_DIRS}
  ${GFlags_INCLUDE_DIRS} ${GTEST_INCLUDE_DIRS})

add_definitions(-DRAPIDJSON_HAS_STDSTRING)

add_library(ranking
  json_parser.cpp
  legecy.cpp)

add_executable(json_parser_test json_parser_test.cpp)

target_link_libraries(json_parser_test
  ranking
  ${GLOG_LIBRARIES}
  ${GFlags_LIBS}
  ${GTEST_LIBRARY}
  ${GTEST_MAIN_LIBRARY})

add_test(json_parser_test json_parser_test)
