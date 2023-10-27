# App flows

## Sales Dispatch

Warehouse -> Picker -> Checker -> Vehicle

### Data preparation

1. Request items [POST] `/inventory/stock_movement/`

### Getting the data for sales taking order

- Get data from `sales/trip/?delivery_ready=true`
- Required parameter: delivery_reade: `true`
- Then for each trip, get the id32 then retrieve the `stock_movemente_id32s` from `sales/trip/<id32>/`
- with stock_movemente_id32s you can retrieve the stock_movement detail

### Getting the data for sales canvasing

- Get data from `inventory/stock_movement/?movement_date_range=2023-10-21%2C2023-10-22&origin_filter=warehouse%2C1&status=requested`
- Required Parameters:
  - movement_date_range: `"YYYY-MM-DD,YYYY-MM-DD"` [today,today+1]
  - origin_filter: `"origin_type,origin_id32"`Example. `"warehouse,A"` (origin_id32 can be retrieved from `warehouse_assignment` in me endpoint)
  - status: `"requested"`
- Optional Parameters:
  - destination_filters: `"destination_type,origin_id32"`Example. `"warehouse,A"`
- The endpoint will return lists of requested stockmovement in specific warehouse

### Progressing for picker dispatch

1. Select a stockmovement from list above at `/inventory/stock_movement/id32/`
2. Look for items that the picker wanna pick, location can be seen at `origin_locations` inside `item` object
3. Look for items that has `waiting` origin_movement_status
4. if the picker pickin up the item, origin_movement_status should be changed to `on_progress`
5. if the picker finished picking the item, and the item has been put to designated location, update the origin_movement_status should be changed to `put`

### Progressing for checker dispatch

1. Select a stockmovement from list above at `/inventory/stock_movement/id32/`
2. Look for items that the checker wanna check
3. Look for items that has `put` origin_movement_status
4. if the checker is checking on the item, origin_movement_status should be changed to `on_check`
5. if the checker finished checking the item, update the origin_movement_status should be changed to `finished`
(stock_movement stock tested: ✅)

## PO Inbound Inbound Movement

PO Inbound: from supplier
Vehicle -> Checker -> Picker -> Warehouse

### Data Preparation

1. Request Purchase Order `POST /purchasing/purchase_order/`
2. Approve the PO `POST /purchasing/purchase_order/<id32>/approve/`

### Getting the data

- Get data from `/inventory/stock_movement/?destination_filter=warehouse%2C1&status=requested`
- Required Parameters:
  - destination_filter: `"destination_type,destination_id32"`Example. `"warehouse,A"` (destination_id32 can be retrieved from `warehouse_assignment` in me endpoint)
  - status: `"requested"`
- Optional Parameters:
  - destination_filters: `"origin_type,origin_id32"`Example. `"warehouse,A"`
- The endpoint will return lists of requested inbound stockmovement in specific warehouse

### Progressing for checker inbound

1. Select a stockmovement from list above at `/inventory/stock_movement/id32/`
2. Look for items that the picker wanna pick
3. Look for items that has `waiting` destination_movement_status
4. if the checker is checking on the item, destination_movement_status should be changed to `on_check`
5. if the checker finished checking the item, update the destination_movement_status should be changed to `checked`

### Progressing for picker inbound

1. Select a stockmovement from list above at `/inventory/stock_movement/id32/`
2. Look for items that the picker wanna pick, location can be seen at `destination_locations` inside `item` object
3. Look for items that has `checked` destination_movement_status
4. if the picker pickin up the item, destination_movement_status should be changed to `on_progress`
5. if the picker finished picking the item, and the item has been put to designated location, update the destination_movement_status should be changed to `put`

## Vehicle Inbound

inbound from internal vehicle (can be from canvasing or other internal warehouse)

## Sales Taking Order

Pick trip -> Create Sales Order -> Continue Trip

## Purchasing

1. Create PO
2. Approve PO
3. Each inbound item - destination status change: `on_check`, `check`, `on_progress`, `put`
(stock_movement stock tested: ✅)
