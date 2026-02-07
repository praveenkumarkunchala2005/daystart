import { createClient } from "@supabase/supabase-js";

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!;
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!;

/**
 * Initialized Supabase client for interacting with the database.
 * Uses the project URL and anonymous key from environment variables.
 */
export const supabase = createClient(supabaseUrl, supabaseAnonKey);
