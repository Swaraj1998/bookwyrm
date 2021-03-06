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

#include <fmt/format.h>

#include "item.hpp"
#include "screens/base.hpp"

/*
 * Interface-wise, this will be like opening an email for reading in mutt.
 * A thread will be spawned to fetch more info about the item from some database,
 * and the bookwyrm will print that info in this window in a pretty way.
 *
 * The user should still be able to check another item's details while this thread is running.
 * Item details will be kept in the actual item. So a passed item will be modified, otherwise,
 * if the user goes back to an item, we'll need to fetch the data again.
 *
 * The user doesn't need to exit the detail screen to select another item for details.
 * Implementing this is a problem for the future, though.
 */
namespace screen {

class item_details : public base {
public:
    explicit item_details(const bookwyrm::item &item, int padding_top);

    bool action(const key &key, const uint32_t &ch) override;
    void paint() override;
    string footer_info() const override;
    int scrollpercent() const override;

    string controls_legacy() const override
    {
        return "[h]Close details";
    }

    void move(move_direction dir)
    {
        /* stub */
        (void)dir;
        return;
    }

private:
    const bookwyrm::item &item_;

    void print_borders();
    void print_details();

    /* Print the item's description from line y and downward. */
    void print_desc(int &y, string str);
};

/* ns screen */
}

