import { Component, OnInit } from '@angular/core';
import {
  FormBuilder,
  FormGroup,
  Validators,
  ReactiveFormsModule,
  AbstractControl,
  ValidationErrors,
  ValidatorFn,
} from '@angular/forms';
import { AuthService } from '../auth.service';
import { Router, RouterModule } from '@angular/router';
import { CommonModule } from '@angular/common';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { MatSelectModule } from '@angular/material/select';
import { MatCardModule } from '@angular/material/card';
import { MatIconModule } from '@angular/material/icon';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatOptionModule } from '@angular/material/core';

@Component({
  selector: 'app-sign-up',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    RouterModule,
    MatInputModule,
    MatButtonModule,
    MatSelectModule,
    MatCardModule,
    MatIconModule,
    MatFormFieldModule,
    MatOptionModule,
  ],
  templateUrl: './sign-up.component.html',
  styleUrls: ['./sign-up.component.scss'],
})
export class SignUpComponent implements OnInit {
  signUpForm!: FormGroup;
  errorMessage: string = '';
  hidePassword = true;
  hideConfirmPassword = true;

  constructor(
    private fb: FormBuilder,
    private authService: AuthService,
    private router: Router
  ) {}

  ngOnInit() {
    this.signUpForm = this.fb.group(
      {
        username: [
          '',
          [
            Validators.required,
            Validators.minLength(3),
            Validators.maxLength(20),
            Validators.pattern('^[a-zA-Z0-9]+$'),
          ],
        ],
        email: ['', [Validators.required, Validators.email]],
        password: ['', [Validators.required, passwordStrengthValidator()]],
        confirmPassword: ['', Validators.required],
        name: [''],
        age: ['', [Validators.min(18)]],
        gender: ['', [Validators.pattern('^(male|female|other)$')]],
        placeOfResidence: [''],
        fieldOfStudy: [''],
      },
      { validators: passwordMatchValidator }
    );
  }

  // Getters for form controls
  get username(): AbstractControl {
    return this.signUpForm.get('username')!;
  }

  get email(): AbstractControl {
    return this.signUpForm.get('email')!;
  }

  get password(): AbstractControl {
    return this.signUpForm.get('password')!;
  }

  get confirmPassword(): AbstractControl {
    return this.signUpForm.get('confirmPassword')!;
  }

  get age(): AbstractControl {
    return this.signUpForm.get('age')!;
  }

  get gender(): AbstractControl {
    return this.signUpForm.get('gender')!;
  }

  onSubmit() {
    if (this.signUpForm.valid) {
      const formValue = { ...this.signUpForm.value };
      delete formValue.confirmPassword;

      this.authService.signUp(formValue).subscribe({
        next: (response) => {
          console.log('User registered successfully', response);
          localStorage.setItem('access_token', response.access_token);
          this.router.navigate(['/dashboard']); // Adjust the route as needed
        },
        error: (error) => {
          console.error('Error registering user', error);
          if (error.status === 409) {
            this.errorMessage =
              'A user with this username or email already exists.';
          } else {
            this.errorMessage = error.error.message || 'Failed to register user.';
          }
        },
      });
    } else {
      this.errorMessage = 'Please correct the errors in the form.';
    }
  }
}

// Custom Validator for Password Strength
function passwordStrengthValidator(): ValidatorFn {
  return (control: AbstractControl): ValidationErrors | null => {
    const value = control.value || '';
    const passwordValid = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[\W_]).{8,}$/.test(
      value
    );
    return passwordValid ? null : { passwordStrength: true };
  };
}

// Custom Validator for Password Match
function passwordMatchValidator(form: AbstractControl): ValidationErrors | null {
  const password = form.get('password')?.value;
  const confirmPassword = form.get('confirmPassword')?.value;
  if (password !== confirmPassword) {
    return { passwordMismatch: true };
  }
  return null;
}
