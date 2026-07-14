import { createContext, useContext } from 'react'

const ScreenersSelectionContext = createContext(null)

export const ScreenersSelectionProvider = ScreenersSelectionContext.Provider

export const useScreenersSelection = () => useContext(ScreenersSelectionContext)
