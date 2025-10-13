// Currency conversion constants
const SATS_PER_BTC = 100000000
const CENTS_PER_USD = 100

export interface CurrencyValidationResult {
  isValid: boolean
  errorMessage?: string
  valueInBaseUnits?: number
}

/**
 * Convert display value to base units (cents or satoshis)
 */
export function parseAmountToBaseUnits(value: string, currency: string): number | null {
  const num = parseFloat(value)
  if (isNaN(num) || num <= 0) return null
  
  if (currency === 'USD') {
    return Math.round(num * CENTS_PER_USD)
  } else if (currency === 'BTC') {
    return Math.round(num * SATS_PER_BTC)
  }
  
  return null
}

/**
 * Convert base units (cents or satoshis) to display value
 */
export function formatBaseUnitsToDisplay(baseUnits: number, currency: string): string {
  if (currency === 'USD') {
    return (baseUnits / CENTS_PER_USD).toFixed(2)
  } else if (currency === 'BTC') {
    // Format BTC with up to 8 decimals, removing trailing zeros
    const btc = baseUnits / SATS_PER_BTC
    return btc.toFixed(8).replace(/\.?0+$/, '') || '0'
  }
  
  return baseUnits.toString()
}

/**
 * Format amount for display with currency symbol
 */
export function formatAmountWithCurrency(baseUnits: number, currency: string): string {
  const value = formatBaseUnitsToDisplay(baseUnits, currency)
  return `${value} ${currency}`
}

/**
 * Validate input precision and provide helpful error messages
 */
export function validateAmountPrecision(value: string | number, currency: string): CurrencyValidationResult {
  // Convert to string to handle both string and number inputs from Vue
  const stringValue = String(value)
  
  // Check if empty or not a number
  if (!stringValue || stringValue.trim() === '') {
    return { isValid: false, errorMessage: 'Amount is required' }
  }
  
  const num = parseFloat(stringValue)
  if (isNaN(num)) {
    return { isValid: false, errorMessage: 'Please enter a valid number' }
  }
  
  if (num <= 0) {
    return { isValid: false, errorMessage: 'Amount must be greater than 0' }
  }
  
  // Check decimal precision
  const decimalMatch = stringValue.match(/\.(\d+)$/)
  const decimalPlaces = decimalMatch ? decimalMatch[1].length : 0
  
  const maxDecimals = currency === 'USD' ? 2 : currency === 'BTC' ? 8 : 2
  
  if (decimalPlaces > maxDecimals) {
    // Calculate nearest valid values
    const factor = currency === 'USD' ? CENTS_PER_USD : SATS_PER_BTC
    const baseUnits = num * factor
    const lower = Math.floor(baseUnits)
    const upper = Math.ceil(baseUnits)
    
    const lowerDisplay = formatBaseUnitsToDisplay(lower, currency)
    const upperDisplay = formatBaseUnitsToDisplay(upper, currency)
    
    return {
      isValid: false,
      errorMessage: `Please enter a valid value. The 2 nearest valid values are ${lowerDisplay} and ${upperDisplay}`
    }
  }
  
  // Valid input - convert to base units
  const baseUnits = parseAmountToBaseUnits(stringValue, currency)
  if (baseUnits === null) {
    return { isValid: false, errorMessage: 'Invalid amount' }
  }
  
  return { isValid: true, valueInBaseUnits: baseUnits }
}

/**
 * Get the appropriate step value for number inputs
 */
export function getInputStep(currency: string): string {
  if (currency === 'USD') return '0.01'
  if (currency === 'BTC') return '0.00000001'
  return 'any'
}