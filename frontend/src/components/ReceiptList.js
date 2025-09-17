import React from 'react';

function ReceiptList({ receipts }) {
  return (
    <div className="card">
      <h2>Recent Receipts ({receipts.length})</h2>
      <div style={{ marginTop: '20px' }}>
        {receipts.map((receipt) => (
          <div key={receipt.receipt_id} className="receipt-item">
            <h3>{receipt.merchant || 'Unknown Merchant'}</h3>
            <p><strong>Date:</strong> {receipt.purchase_date}</p>
            <p><strong>Time:</strong> {receipt.purchase_time || 'N/A'}</p>
            <p><strong>Amount:</strong> <span className="amount">€{receipt.total_amount}</span></p>
            <p><strong>Category:</strong> {receipt.category || 'Other'}</p>
            <p><strong>File:</strong> {receipt.file_name}</p>
          </div>
        ))}
      </div>
    </div>
  );
}

export default ReceiptList;