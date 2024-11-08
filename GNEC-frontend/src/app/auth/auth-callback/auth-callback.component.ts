// auth-callback.component.ts
import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { CommonModule } from '@angular/common';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner'; // Import the spinner module

@Component({
  selector: 'app-auth-callback',
  standalone: true, // Marking the component as standalone
  imports: [CommonModule, MatProgressSpinnerModule], // Include the spinner module here
  template: `
    <div class="auth-callback-container">
      <mat-progress-spinner mode="indeterminate"></mat-progress-spinner>
      <p>Signing you in...</p>
    </div>
  `,
  styleUrls: ['./auth-callback.component.scss'],
})
export class AuthCallbackComponent implements OnInit {
  constructor(
    private route: ActivatedRoute,
    private router: Router
  ) {}

  ngOnInit(): void {
    this.route.queryParams.subscribe(params => {
      const token = params['token'];
      const userId = params['userId'];
      const error = params['error'];

      if (error) {
        this.router.navigate(['/auth/sign-in'], { queryParams: { error: 'Authentication failed. Please try again.' } });
        return;
      }

      if (token && userId) {
        localStorage.setItem('access_token', token);
        localStorage.setItem('user_id', userId);
        this.router.navigate(['/']); // Adjust the route as needed
      } else {
        // Handle missing token or userId
        this.router.navigate(['/auth/sign-in'], { queryParams: { error: 'Authentication failed. Please try again.' } });
      }
    });
  }
}
