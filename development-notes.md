# Development notes and to do

- if trip is canvasing and salesperson not requested stock movement, then able to checkout should still False
- StockMovement update warehouse stock still bug, if origin is none movement still proceeded

## To Do

- Taking order endpoint direview lagi ✅
- Picker endpoint ✅
- Checker endpont ✅
- StockMovementItem detail view ✅
- Endpoint batch di stockmovement item ✅
- Foto barang endpoint untuk complete checker sales ✅
- Surat jalan
- Picker Checker untuk Taking Order ✅
- Endpoint barang tidak sesuai ✅
- Endpoint sisa penjualan ✅
- handle_origin_warehouse bug: Harusnya hanya deduct jika sales canvasing dan destination customer
(STOCK MOVEMENT add and deduct stock harus dicek lagi flow nya, beberapa deprecated) ✅
- Endbpoint batch product inbound beserta expire date nya ✅
- Keluarin SKU di stock movement item dan filter SKU di product ✅
- Trip Report endpoint
- Implode/explode endpoints

## TBC

- Explode flows - Di gudang sesuai fisik
  - Canvasing: Ngubah sendiri di pas jual (otomatis berdasarkan inputan si sales canvasing)
  - Pengiriman Taking order: Sama si picker
- Surat jalan (diprint dimana?) - diprint di admin per customer
- Dokumen serah terima barang (diprint dimana?) - diprint di admin, untuk semua barang di mobil
- Market oportunity for catering: sales commision

Stock Opname:
- Gudang
- Barang apa aja
- Quantity berapa

Admin stock opname gak bisa lihat quantity data, cuman bisa opname

Audit:
- Histori penjualan
- Histori piutang
  - Daftar nunggak
- Audit stok barang (stock opname)


