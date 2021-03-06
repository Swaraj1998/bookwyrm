# Copyright (C) 2017 Tmplt <tmplt@dragons.rocks>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

set(SOURCE
    ${SOURCE}
    main.cpp
    item.cpp
    utils.cpp
    keys.cpp
    components/logger.cpp
    components/command_line.cpp
    components/script_butler.cpp
    components/screen_butler.cpp
    components/downloader.cpp
    screens/base.cpp
    screens/multiselect_menu.cpp
    screens/item_details.cpp
    screens/log.cpp
)


# Include-order matters; if there is a header clash, the project-local headers are used.
set(APP_INCLUDE_DIRS ${APP_INCLUDE_DIRS} ${PROJECT_SOURCE_DIR}/include)
set(APP_INCLUDE_DIRS ${APP_INCLUDE_DIRS} ${CMAKE_CURRENT_BINARY_DIR})

# Required dependencies:
set(THREADS_PREFER_PTHREAD_FLAG ON)
find_package(Threads REQUIRED QUIET)

set(APP_LIBRARIES ${APP_LIBRARIES} ${CMAKE_THREAD_LIBS_INIT})
set(APP_INCLUDE_DIRS ${APP_INCLUDE_DIRS} ${PROJECT_SOURCE_DIR}/lib/spdlog/include)
set(APP_INCLUDE_DIRS ${APP_INCLUDE_DIRS} ${PROJECT_SOURCE_DIR}/lib/fmt/)
set(APP_INCLUDE_DIRS ${APP_INCLUDE_DIRS} ${PROJECT_SOURCE_DIR}/lib/fuzzywuzzy/include)
set(APP_INCLUDE_DIRS ${APP_INCLUDE_DIRS} ${PROJECT_SOURCE_DIR}/lib/pybind11/include)
set(APP_INCLUDE_DIRS ${APP_INCLUDE_DIRS} ${PROJECT_SOURCE_DIR}/lib/termbox/src)
set(APP_INCLUDE_DIRS ${APP_INCLUDE_DIRS} ${CPR_INCLUDE_DIRS})

# Some pre-compile tasks:
execute_process(COMMAND git describe --tags --dirty=-git
  WORKING_DIRECTORY ${PROJECT_BINARY_DIR}
  OUTPUT_VARIABLE PROG_VERSION
  OUTPUT_STRIP_TRAILING_WHITESPACE ERROR_QUIET)

configure_file(
  ${PROJECT_SOURCE_DIR}/include/version.hpp.cmake
  ${CMAKE_SOURCE_DIR}/include/version.hpp
  ESCAPE_QUOTES @ONLY)

# Make the thing.
make_executable(${PROJECT_NAME}
    SOURCES
      ${SOURCE}
    INCLUDE_DIRS
      ${APP_INCLUDE_DIRS}
    RAW_DEPENDS
      ${APP_LIBRARIES})

target_link_libraries(${PROJECT_NAME}
    Threads::Threads
    fmt
    fuzzywuzzy
    pybind11::embed
    stdc++fs
    termbox_lib_static
    curl)

add_subdirectory(bindings)
