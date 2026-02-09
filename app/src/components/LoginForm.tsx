import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Activity, Loader2 } from 'lucide-react';

interface LoginFormProps {
  onLogin: (username: string, password: string) => void;
  isLoading: boolean;
}

export function LoginForm({ onLogin, isLoading }: LoginFormProps) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onLogin(username, password);
  };

  return (
    <Card className="w-full max-w-md shadow-2xl border-0">
      <CardHeader className="space-y-4 text-center pb-8">
        <div className="mx-auto bg-blue-500 w-16 h-16 rounded-2xl flex items-center justify-center shadow-lg">
          <Activity className="h-8 w-8 text-white" />
        </div>
        <div>
          <CardTitle className="text-2xl font-bold text-slate-900">
            Chemical Equipment Visualizer
          </CardTitle>
          <CardDescription className="text-slate-500 mt-2">
            Sign in to access your equipment data
          </CardDescription>
        </div>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="username" className="text-slate-700">Username</Label>
            <Input
              id="username"
              type="text"
              placeholder="Enter your username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
              className="h-11"
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="password" className="text-slate-700">Password</Label>
            <Input
              id="password"
              type="password"
              placeholder="Enter your password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              className="h-11"
            />
          </div>
          <Button 
            type="submit" 
            className="w-full h-11 text-base font-medium"
            disabled={isLoading}
          >
            {isLoading ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Signing in...
              </>
            ) : (
              'Sign In'
            )}
          </Button>
        </form>
        <div className="mt-6 text-center text-sm text-slate-500">
          <p>Default credentials:</p>
          <p className="font-mono bg-slate-100 px-2 py-1 rounded mt-1 inline-block">
            admin / admin
          </p>
        </div>
      </CardContent>
    </Card>
  );
}
