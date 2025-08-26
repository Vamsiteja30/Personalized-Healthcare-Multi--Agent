import { create } from "zustand";

interface UserState {
  userId: number;
  setUserId: (id: number) => void;
}

export const useUserStore = create<UserState>((set) => ({
  userId: 1,
  setUserId: (id: number) => set({ userId: id }),
}));
