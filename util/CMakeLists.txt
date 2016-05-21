aux_source_directory(. UTIL_SRCS)

add_library(util ${UTIL_SRCS})

include_directories(${LIBMEMCACHED_INCLUDE_DIRS})
