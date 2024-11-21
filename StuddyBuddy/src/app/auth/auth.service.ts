import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { BehaviorSubject, Observable, Subject } from 'rxjs';
import { Router } from '@angular/router';
import { environment } from '../shared/constant/environment';
@Injectable({
  providedIn: 'root',
})
export class AuthService {
  private baseUrl = environment.baseUrl; 

  constructor(private http: HttpClient, private router: Router) {}

  signUp(userData: any): Observable<any> {
    return this.http.post(`${this.baseUrl}/user/signup`, userData);
  }

  signIn(credentials: { identifier: string; password: string }): Observable<any> {
    return this.http.post(`${this.baseUrl}/user/login`, credentials);
  }

  requestPasswordReset(email: string): Observable<any> {
    return this.http.post(`${this.baseUrl}/user/request_reset`, { email });
  }

  resetPassword(token: string, password: string): Observable<any> {
    return this.http.post(`${this.baseUrl}/user/reset_password/${token}`, { password });
  }



  // Optional: Method to check if user is authenticated
  isAuthenticated(): boolean {
    return !!localStorage.getItem('access_token');
  }

  // Optional: Method to log out the user
  signOut() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user_id');
    this.router.navigate(['/auth/sign-in']);
  }

   subjectsubscribe = new Subject<number>();
   behavioutsubscribe = new BehaviorSubject([]);

}