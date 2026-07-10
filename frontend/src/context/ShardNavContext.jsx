import { createContext, useContext } from 'react'

const ShardNavContext = createContext(null)

export const ShardNavProvider = ShardNavContext.Provider

export const useShardNav = () => useContext(ShardNavContext)
