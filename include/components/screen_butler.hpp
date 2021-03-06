/*
 * Copyright (C) 2017 Tmplt <tmplt@dragons.rocks>
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 */

#pragma once

#include "common.hpp"
#include "item.hpp"
#include "python.hpp"
#include "colours.hpp"
#include "components/script_butler.hpp"
#include "components/logger.hpp"
#include "screens/base.hpp"
#include "screens/multiselect_menu.hpp"
#include "screens/item_details.hpp"
#include "screens/log.hpp"

/* Circular dependency guard. */
namespace logger { class bookwyrm_logger; }
using logger_t = std::shared_ptr<logger::bookwyrm_logger>;

namespace butler {

/* Circular dependency guard. */
class script_butler;

/*
 * Another butler. This one handles whatever screens we want to show the user,
 * as well as which of them to update. User input post-cli is also handled here,
 * which is forwarded to the currently focused screen unless it was used to
 * manage screens.
 */
class screen_butler {
public:
    /* WARN: this constructor should only be used in make_with() above. */
    explicit screen_butler(vector<bookwyrm::item> &items, logger_t logger);

    /* Repaint all screens that need updating. */
    void repaint_screens();

    /* Send a log entry to the log screen. */
    void log_entry(spdlog::level::level_enum level, const string entry)
    {
        log_->log_entry(level, entry);
        repaint_screens();
    }

    /*
     * Display the TUI and let the user enter input.
     * The input is forwarded to the appropriate screen.
     * Returns false if user wants the program to exit without downloading anything.
     * Returns true otherwise.
     */
    bool display();

    /* Take ownership of the wanted items and move them to the caller. */
    vector<bookwyrm::item> get_wanted_items();

    /* Draw the context sensitive footer. */
    void print_footer();

    bool is_log_focused() const
    {
        return focused_ == log_;
    }

private:
    /* Forwarded to the multiselect menu. */
    vector<bookwyrm::item> const &items_;

    /* Used to flush stored logs to the log screen. */
    logger_t logger_;

    std::shared_ptr<screen::multiselect_menu> index_;
    std::shared_ptr<screen::item_details> details_;
    std::shared_ptr<screen::log> log_;

    std::shared_ptr<screen::base> focused_, last_;

    /* Is a screen::item_details open? */
    bool viewing_details_;

    /* When we close the screen::item_details, how much does the index menu scroll back? */
    int index_scrollback_ = -1;

    /* Returns false if bookwyrm doesn't fit in the terminal window. */
    static bool bookwyrm_fits();

    /* Manage screens. Return true if an action was performed. */
    bool meta_action(const key &key, const uint32_t &ch);

    /*
     * Open a screen::item_details for the currently selected item in the index menu.
     * Returns true if the operation was successful (no detail screen is already open).
     */
    bool open_details();

    /* And close it. Return true if the operation was successful. */
    bool close_details();

    bool toggle_log();

    void resize_screens();

    /* copy from screen::base. */
    static void wprint(int x, const int y, const string_view &str, const colour attrs = colour::white);

    /*
     * Print passed string starting from (x, y) along the x-axis.
     * All other cells on the same line will be empty (' ') with
     * attrs applied.
     */
    static void wprintcont(int x, const int y, const string_view &str, const colour attrs = colour::white);
    static void wprintcont(int x, const int y, const string_view &str, const attribute attr)
    {
        wprintcont(x, y, str, colour::white | attr);
    }
};

/* ns butler */
}

namespace tui {

std::shared_ptr<butler::screen_butler> make_with(butler::script_butler &script_butler, vector<py::module> &seekers, logger_t &logger);

/* ns tui */
}
