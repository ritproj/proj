import React, { useRef, useState } from 'react'
import { UploadCloud, FileText, AlertCircle, CheckCircle2 } from 'lucide-react'

const REQUIRED_COLUMNS = ['Customer_ID', 'Latitude', 'Longitude', 'Demand']
// MVP demo size limit before clustering notice kicks in
const QUANTUM_CUSTOMER_LIMIT = 8

/**
 * Parses a CSV string and returns { rows, error, showClusteringNotice }
 */
function parseCSV(text) {
  const lines = text.trim().split('\n').filter(Boolean)
  if (lines.length < 2) return { rows: null, error: 'CSV file is empty or has no data rows.' }

  const headers = lines[0].split(',').map((h) => h.trim())
  const missing = REQUIRED_COLUMNS.filter((c) => !headers.includes(c))
  if (missing.length > 0) {
    return { rows: null, error: `Missing required columns: ${missing.join(', ')}` }
  }

  const rows = []
  for (let i = 1; i < lines.length; i++) {
    const values = lines[i].split(',').map((v) => v.trim())
    const row = {}
    headers.forEach((h, idx) => { row[h] = values[idx] })
    const demand = parseFloat(row['Demand'])
    if (isNaN(demand) || demand <= 0) {
      return { rows: null, error: `Row ${i + 1}: Demand must be a positive number (got "${row['Demand']}").` }
    }
    rows.push(row)
  }

  const showClusteringNotice = rows.length > QUANTUM_CUSTOMER_LIMIT

  return { rows, error: null, showClusteringNotice }
}

/**
 * UploadBox — drag-and-drop / click to upload CSV.
 * Props:
 *   onFileAccepted(file, rows, showClusteringNotice) — called when validation passes
 *   onError(message) — called when validation fails
 */
export default function UploadBox({ onFileAccepted, onError }) {
  const inputRef = useRef(null)
  const [dragOver, setDragOver] = useState(false)
  const [fileName, setFileName] = useState(null)
  const [valid, setValid] = useState(false)

  function handleFile(file) {
    if (!file) return

    if (!file.name.endsWith('.csv')) {
      setValid(false)
      setFileName(file.name)
      onError('Only .csv files are accepted.')
      return
    }

    const reader = new FileReader()
    reader.onload = (e) => {
      const { rows, error, showClusteringNotice } = parseCSV(e.target.result)
      setFileName(file.name)
      if (error) {
        setValid(false)
        onError(error)
      } else {
        setValid(true)
        onError(null)
        onFileAccepted(file, rows, showClusteringNotice)
      }
    }
    reader.readAsText(file)
  }

  function onInputChange(e) {
    handleFile(e.target.files[0])
  }

  function onDrop(e) {
    e.preventDefault()
    setDragOver(false)
    handleFile(e.dataTransfer.files[0])
  }

  return (
    <div
      onClick={() => inputRef.current?.click()}
      onDragOver={(e) => { e.preventDefault(); setDragOver(true) }}
      onDragLeave={() => setDragOver(false)}
      onDrop={onDrop}
      className={`relative border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-colors duration-200 select-none
        ${dragOver ? 'border-green-400 bg-green-900/20' : 'border-gray-600 bg-gray-800/50 hover:border-gray-500 hover:bg-gray-800'}`}
    >
      <input
        ref={inputRef}
        type="file"
        accept=".csv"
        className="hidden"
        onChange={onInputChange}
      />

      {!fileName ? (
        <>
          <UploadCloud size={36} className="mx-auto text-gray-500 mb-3" />
          <p className="text-gray-300 font-medium">Drag & drop your CSV here</p>
          <p className="text-gray-500 text-sm mt-1">or click to browse</p>
          <p className="text-gray-600 text-xs mt-3">Required columns: Customer_ID, Latitude, Longitude, Demand</p>
        </>
      ) : (
        <div className="flex items-center justify-center gap-3">
          {valid ? (
            <CheckCircle2 size={22} className="text-green-400 shrink-0" />
          ) : (
            <AlertCircle size={22} className="text-red-400 shrink-0" />
          )}
          <FileText size={18} className="text-gray-400 shrink-0" />
          <span className={`font-medium truncate max-w-xs ${valid ? 'text-green-300' : 'text-red-300'}`}>
            {fileName}
          </span>
        </div>
      )}
    </div>
  )
}
