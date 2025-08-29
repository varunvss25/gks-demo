import React, { useEffect, useState } from 'react'
import { getTopCFR, getIssuingOffices, getLetters, getLineage, getTopCFRTrend } from './api'
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, LineChart, Line, CartesianGrid } from 'recharts'

function downloadCSV(rows: any[], filename: string) {
  const header = Object.keys(rows[0] || {}).join(',')
  const body = rows.map(r => Object.values(r).join(',')).join('\n')
  const csv = [header, body].join('\n')
  const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' })
  const link = document.createElement('a')
  link.href = URL.createObjectURL(blob)
  link.setAttribute('download', filename)
  document.body.appendChild(link); link.click(); document.body.removeChild(link)
}

export default function App() {
  const today = new Date().toISOString().slice(0,10)
  const [start, setStart] = useState('2024-01-01')
  const [end, setEnd] = useState(today)
  const [productType, setProductType] = useState('')
  const [top, setTop] = useState<any[]>([])
  const [offices, setOffices] = useState<any[]>([])
  const [letters, setLetters] = useState<any[]>([])
  const [lineage, setLineage] = useState<any[]>([])
  const [trend, setTrend] = useState<any>({ codes: [], series: [] })

  const load = async () => {
    const base:any = { start, end }
    const pt:any = productType ? { product_type: productType } : {}
    setTop(await getTopCFR({ ...base, ...pt }))
    setOffices(await getIssuingOffices(base))
    setLetters(await getLetters({ ...base, ...pt }))
    setLineage(await getLineage())
    setTrend(await getTopCFRTrend({ ...base, ...pt }))
  }
  useEffect(()=>{ load() }, [])

  return (
    <div style={{ fontFamily:'Inter, system-ui, sans-serif', padding:16, maxWidth:1100, margin:'0 auto' }}>
      <h1 style={{ fontSize:28, marginBottom:8 }}>GKS Demo — FDA Warning Letters</h1>
      <div style={{ display:'grid', gridTemplateColumns:'repeat(4,1fr)', gap:12 }}>
        <label>Start <input type='date' value={start} onChange={e=>setStart(e.target.value)} /></label>
        <label>End <input type='date' value={end} onChange={e=>setEnd(e.target.value)} /></label>
        <label>Product Type
          <select value={productType} onChange={e=>setProductType(e.target.value)}>
            <option value=''>All</option><option>Drugs</option><option>Biologics</option><option>Devices</option><option>Foods</option>
          </select>
        </label>
        <button onClick={load} style={{ alignSelf:'end' }}>Apply</button>
      </div>

      <div style={{ display:'grid', gridTemplateColumns:'1fr 1fr', gap:16, marginTop:20 }}>
        <div style={{ height:300, border:'1px solid #e5e5e5', borderRadius:12, padding:12 }}>
          <h3 style={{ margin:0 }}>Top CFR Codes</h3>
          <ResponsiveContainer width='100%' height='90%'>
            <BarChart data={top}><CartesianGrid strokeDasharray='3 3'/><XAxis dataKey='cfr_code'/><YAxis/><Tooltip/><Bar dataKey='count'/></BarChart>
          </ResponsiveContainer>
        </div>
        <div style={{ height:300, border:'1px solid #e5e5e5', borderRadius:12, padding:12 }}>
          <h3 style={{ margin:0 }}>Issuing Offices (Count)</h3>
          <ResponsiveContainer width='100%' height='90%'>
            <BarChart data={offices}><CartesianGrid strokeDasharray='3 3'/><XAxis dataKey='issuing_office'/><YAxis/><Tooltip/><Bar dataKey='count'/></BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div style={{ height:320, border:'1px solid #e5e5e5', borderRadius:12, padding:12, marginTop:20 }}>
        <h3 style={{ margin:0 }}>Top CFR Trend</h3>
        <ResponsiveContainer width='100%' height='85%'>
          <LineChart data={trend.series}><CartesianGrid strokeDasharray='3 3'/><XAxis dataKey='period'/><YAxis/><Tooltip/>{trend.codes.map((c:string)=>(<Line key={c} type='monotone' dataKey={c} dot={false}/>))}</LineChart>
        </ResponsiveContainer>
      </div>

      <div style={{ marginTop:20, border:'1px solid #e5e5e5', borderRadius:12, padding:12 }}>
        <div style={{ display:'flex', justifyContent:'space-between', alignItems:'center' }}>
          <h3 style={{ margin:0 }}>Letters</h3>
          <button onClick={()=> letters.length && downloadCSV(letters,'letters.csv')}>Download CSV</button>
        </div>
        <table style={{ width:'100%', borderCollapse:'collapse' }}>
          <thead><tr><th style={{textAlign:'left',borderBottom:'1px solid #ddd',padding:8}}>Date</th><th style={{textAlign:'left',borderBottom:'1px solid #ddd',padding:8}}>Firm</th><th style={{textAlign:'left',borderBottom:'1px solid #ddd',padding:8}}>Product</th><th style={{textAlign:'left',borderBottom:'1px solid #ddd',padding:8}}>Office</th><th style={{textAlign:'left',borderBottom:'1px solid #ddd',padding:8}}>URL</th></tr></thead>
          <tbody>{letters.map((l:any,i:number)=>(<tr key={i}><td style={{borderBottom:'1px solid #f0f0f0',padding:8}}>{l.issue_date}</td><td style={{borderBottom:'1px solid #f0f0f0',padding:8}}>{l.firm}</td><td style={{borderBottom:'1px solid #f0f0f0',padding:8}}>{l.product_type}</td><td style={{borderBottom:'1px solid #f0f0f0',padding:8}}>{l.issuing_office}</td><td style={{borderBottom:'1px solid #f0f0f0',padding:8}}><a href={l.url} target='_blank'>open</a></td></tr>))}</tbody>
        </table>
      </div>
    </div>
  )
}
