import { useEffect, useState } from 'react'

// Runs an API call and tracks its state. Pass `null` as the call to skip it.
// Returns { data, error, loading }.
export function useApi(call, deps) {
  const [state, setState] = useState({ data: null, error: null, loading: false })

  useEffect(() => {
    if (!call) return
    let cancelled = false
    setState({ data: null, error: null, loading: true })
    call()
      .then((data) => !cancelled && setState({ data, error: null, loading: false }))
      .catch((error) => !cancelled && setState({ data: null, error, loading: false }))
    return () => {
      cancelled = true
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, deps)

  return state
}
