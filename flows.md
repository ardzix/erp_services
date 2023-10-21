# Dispatch Picker

**Data preparation**
1. Request items [POST] `/inventory/stock_movement/`


**Getting the data**
- Get data from `inventory/stock_movement/?movement_date_range=2023-10-21%2C2023-10-22&origin_filter=warehouse%2C1&status=requested`
- Required Parameters:
    - movement_date_range: `"YYYY-MM-DD,YYYY-MM-DD"` [today,today+1]
    - origin_filter: `"origin_type,origin_id32"`Example. `"warehouse,A"` (origin_id32 can be retrieved from `warehouse_assignment` in me endpoint)
    - status: `"requested"`
- Optional Parameters:
    - destination_filters: `"destination_type,origin_id32"`Example. `"warehouse,A"`
- The endpoint will return lists of requested stockmovement in specific warehouse

**Progressing for picker**
1. Select a stockmovement from list above at `/inventory/stock_movement/id32/`
2. Look for items that the picker wanna pick, location can be seen at `origin_locations` inside `item` object
3. Look for items that has `waiting` origin_movement_status
4. if the picker pickin up the item, origin_movement_status should be changed to `on_progress`
5. if the picker finished picking the item, and the item has been put to designated location, update the origin_movement_status should be changed to `put`

**Progressing for checker**
1. Select a stockmovement from list above at `/inventory/stock_movement/id32/`
2. Look for items that the picker wanna pick
3. Look for items that has `put` origin_movement_status
4. if the checker is checking on the item, origin_movement_status should be changed to `on_check`
5. if the checker finished checking the item, update the origin_movement_status should be changed to `finished`