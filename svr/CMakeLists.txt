add_executable(ranksvr main.cpp )

include_directories(../http)

target_link_libraries(ranksvr
  http pthread boost_system boost_thread)
