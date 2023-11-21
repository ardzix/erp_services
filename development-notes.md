# Development notes and to do

- if trip is canvasing and salesperson not requested stock movement, then able to checkout should still False
- StockMovement update warehouse stock still bug, if origin is none movement still proceeded

## To Do

- Trip Report endpoint
- Implode/explode endpoints
- Auto explode on sales order ✅
- Transaction endpoints ✅
- Journal endpoint (View only) ✅
- Transaction and journal adjustment

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


