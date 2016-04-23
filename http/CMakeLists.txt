include_directories(${GLOG_INCLUDE_DIRS} ${GFlags_INCLUDE_DIRS})

aux_source_directory(. HTTP_SRCS)

add_library(http ${HTTP_SRCS})
