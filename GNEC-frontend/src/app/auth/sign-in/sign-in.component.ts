// sign-in.component.ts
import { Component, OnInit, NgZone } from '@angular/core';
import {
  FormBuilder,
  FormGroup,
  Validators,
  ReactiveFormsModule,
  AbstractControl,
} from '@angular/forms';
import { AuthService } from '../auth.service';
import { RouterModule, Router } from '@angular/router';
import { CommonModule } from '@angular/common';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatIconModule } from '@angular/material/icon';
import { MatFormFieldModule } from '@angular/material/form-field';
import { environment } from '../../../environments/environment';
@Component({
  selector: 'app-sign-in',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    RouterModule,
    MatInputModule,
    MatButtonModule,
    MatCardModule,
    MatIconModule,
    MatFormFieldModule,
  ],
  templateUrl: './sign-in.component.html',
  styleUrls: ['./sign-in.component.scss'],
})
export class SignInComponent implements OnInit {
  signInForm!: FormGroup;
  errorMessage: string = '';
  hidePassword = true;

  constructor(
    private fb: FormBuilder,
    private authService: AuthService,
    private router: Router,
    private ngZone: NgZone
  ) {}

  ngOnInit() {
    this.signInForm = this.fb.group({
      identifier: ['', Validators.required],
      password: ['', Validators.required],
    });

    // Listen for messages from the Google OAuth popup
    window.addEventListener('message', this.handleMessage.bind(this), false);
  }

  // Getters for form controls
  get identifier(): AbstractControl {
    return this.signInForm.get('identifier')!;
  }

  get password(): AbstractControl {
    return this.signInForm.get('password')!;
  }

  onSubmit() {
    if (this.signInForm.invalid) {
      return;
    }

    this.authService.signIn(this.signInForm.value).subscribe({
      next: (response) => {
        localStorage.setItem('access_token', response.access_token);
        localStorage.setItem('user_id', response.userId);
        this.router.navigate(['/dashboard']); // Adjust the route as needed
      },
      error: (error) => {
        this.errorMessage = error.error.msg || 'Invalid identifier or password';
      },
    });
  }

  signInWithGoogle() {
    const googleAuthUrl = `${environment.baseUrl}/auth/google`;

    window.open(
      googleAuthUrl,
      'GoogleAuth'
    );
  }

  private handleMessage(event: MessageEvent) {
    // Ensure the message is coming from a trusted origin
    const trustedOrigin = window.location.origin;
    if (event.origin !== trustedOrigin) {
      return;
    }

    const data = event.data;
    console.log('Received message:', data);
    if (data.type === 'google-auth' && data.token) {
      this.ngZone.run(() => {
        localStorage.setItem('access_token', data.token);
        localStorage.setItem('user_id', data.userId);
        this.router.navigate(['/dashboard']); // Adjust the route as needed
      });
    }
  }
}
