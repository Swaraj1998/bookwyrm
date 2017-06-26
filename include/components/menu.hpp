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

#include <termbox.h>

#include <set>
#include <mutex>
#include <array>
#include <tuple>
#include <utility>
#include <variant>

#include "common.hpp"
#include "item.hpp"

namespace bookwyrm {

class menu {
public:
    explicit menu(vector<item> &items);
    ~menu();

    /* Fires up the menu. */
    void display();

    /* Updates the menu entries to match those in items_. */
    void update();

private:
    enum move_direction { top, up, down, bot };

    /* Store data about each column between updates. */
    struct columns_t {

        struct column_t {
            using width_w_t = std::variant<int, double>;

            /*
             * width_w(wanted).
             * How much space does the column want?
             * Can be specified as an absolute value or
             * as a multiplier, e.g. 0.30 for 30% of tb_width().
             */
            width_w_t width_w;

            /* Changes whenever the window dimensions are changed. */
            size_t width;
            string title;
        };

        void operator=(vector<std::pair<string, column_t::width_w_t>> &&pairs)
        {
            int i = 0;
            for (auto &&pair : pairs) {
                columns_[i].width_w = std::get<1>(pair);
                columns_[i++].title = std::get<0>(pair);
            }
        }

        auto begin() { return columns_.begin(); }
        auto end()   { return columns_.end();   }

    private:
        std::array<column_t, 6> columns_;
    } columns_;

    /* How much space do we leave for bars? */
    const int padding_top_, padding_bot_, padding_right_;

    /* Index of the currently selected item. */
    size_t selected_item_;

    /* How many lines have we scrolled? */
    size_t scroll_offset_;

    std::mutex menu_mutex_;
    vector<item> const &items_;

    /* Item indices marked for download. */
    std::set<int> marked_items_;

    size_t item_count() const
    {
        return items_.size();
    }

    bool is_marked(size_t idx) const
    {
        return marked_items_.find(idx) != marked_items_.cend();
    }

    /* How many entries can the menu print in the terminal? */
    size_t menu_capacity() const
    {
        return tb_height() - padding_bot_ - padding_top_;
    }

    /*
     * Is the currently selected item the last one in the
     * menu "window"?
     */
    bool menu_at_bot() const
    {
        return selected_item_ == (menu_capacity() - 1 + scroll_offset_);
    }

    /*
     * Is the currently selected item the first one in the
     * menu "window"?
     */
    bool menu_at_top() const
    {
        return selected_item_ == scroll_offset_;
    }

    /* Prints an item across the passed y-coordinate. */
    void print_item(const item &t, const size_t y);

    /* From Ncurses. */
    void mvprintw(int x, int y, string str);

    /* Move up and down the menu. */
    void move(move_direction dir);

    /* Select (or unselect) the current item for download. */
    void toggle_select();

    void mark_item(size_t idx)
    {
        marked_items_.insert(idx);
    }

    void unmark_item(size_t idx)
    {
        marked_items_.erase(idx);
    }

    void init_tui();

    /* A few things we need to do on a resize event. */
    void update_column_widths();
    void on_resize();

    void print_scrollbar();
    void print_header();
};

} /* ns bookwyrm */
