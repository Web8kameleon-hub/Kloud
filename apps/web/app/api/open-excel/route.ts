/**
 * API Route: Open Excel File
 * Hap skedarin Excel në desktop
 */

import { NextRequest, NextResponse } from 'next/server'
import { exec } from 'child_process'
import path from 'path'

export async function GET(request: NextRequest) {
  const { searchParams } = new URL(request.url)
  const filename = searchParams.get('file')
  
  if (!filename) {
    return NextResponse.json({ error: 'Missing file parameter' }, { status: 400 })
  }
  
  // Rruga e skedarit
  const filePath = path.join('C:', 'Users', 'Admin', 'Desktop', 'Kloud-cloud', filename)
  
  try {
    // Përdor PowerShell për të hapur skedarin (më i mirë për Windows)
    const command = `powershell -Command "Start-Process '${filePath}'"`
    
    exec(command, (error) => {
      if (error) {
        console.error('Error opening Excel:', error)
      }
    })
    
    return NextResponse.json({ 
      success: true, 
      message: `Opening ${filename}`,
      path: filePath 
    })
  } catch (error) {
    return NextResponse.json({ 
      error: 'Failed to open file',
      details: String(error)
    }, { status: 500 })
  }
}

