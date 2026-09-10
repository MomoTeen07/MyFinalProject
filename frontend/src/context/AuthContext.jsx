import {createContext,useContext,useEffect,useState} from 'react';
import {api} from '../api/client';
const AuthContext=createContext(null);
export function AuthProvider({children}){
 const [user,setUser]=useState(null); const [loading,setLoading]=useState(true);
 useEffect(()=>{ if(localStorage.getItem('token')) api('/api/users/me').then(setUser).catch(()=>localStorage.removeItem('token')).finally(()=>setLoading(false)); else setLoading(false)},[]);
 const login=async(email,password)=>{const d=await api('/api/auth/login',{method:'POST',body:JSON.stringify({email,password})});localStorage.setItem('token',d.access_token);setUser(await api('/api/users/me'));};
 const register=async(name,email,password)=>{const d=await api('/api/auth/register',{method:'POST',body:JSON.stringify({name,email,password})});localStorage.setItem('token',d.access_token);setUser(await api('/api/users/me'));};
 const logout=()=>{localStorage.removeItem('token');setUser(null)};
 return <AuthContext.Provider value={{user,loading,login,register,logout}}>{children}</AuthContext.Provider>
}
export const useAuth=()=>useContext(AuthContext);
