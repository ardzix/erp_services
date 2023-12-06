# Development notes and to do

- if trip is canvasing and salesperson not requested stock movement, then able to checkout should still False
- StockMovement update warehouse stock still bug, if origin is none movement still proceeded

## To Do

- Redefine purchase order filter for inbound in checker and picker ✅
- Create endpoint able to checkout for admin ✅
- Able checkot driver masih belum terimplementasi
- Able checkout picker buggy, harus dicek lagi
- Create location tracker endpoint
- PO stock_movement items bugs on its property and stock creation
- If inboud check (sisa penjualan) item is difeerent in item stock, than add stock adjustment data
- PIC location on on going trip ✅
- Implode/explode endpoints
- Trip Report endpoint
- Checker inbound if stock movement item is not same as phsycal item
- Auto explode on sales order ✅
- Transaction endpoints ✅
- Journal endpoint (View only) ✅
- Transaction and journal adjustment
- Tracking endpoint to periodicallu track employee

## Notes

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


