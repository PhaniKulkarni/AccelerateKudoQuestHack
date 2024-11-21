// sign-in.component.ts
import { Component, OnInit, NgZone } from '@angular/core';
import {
  FormGroup,
  Validators,
  ReactiveFormsModule,
  AbstractControl,
  FormControl,
} from '@angular/forms';
import { AuthService } from '../auth.service';
import { RouterModule, Router } from '@angular/router';
import { CommonModule } from '@angular/common';
import { environment } from 'src/app/shared/constant/environment';
@Component({
  selector: 'app-sign-in',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    RouterModule,
  ],
  templateUrl: './sign-in.component.html',
  styleUrls: ['./sign-in.component.scss'],
})
export class SignInComponent implements OnInit {
  signInForm!: FormGroup;
  errorMessage: string = '';
  hidePassword = true;
  submitted = false;
  showPassword: any = false;

  constructor(
    private authService: AuthService,
    private router: Router,
    private ngZone: NgZone
  ) {}

  ngOnInit() {
    this.signInForm = new FormGroup({
      identifier: new FormControl('', [Validators.required,Validators.email]) ,
      password: new FormControl('', Validators.required),
    });

    // window.addEventListener('message', this.handleMessage.bind(this), false);

    // this.authService.subjectsubscribe.subscribe((value:any)=>{
    //   console.log(value,"value")
    // })
  }

  // Getters for form controls
  // get identifier(): AbstractControl {
  //   return this.signInForm.get('identifier')!;
  // }

  // get password(): AbstractControl {
  //   return this.signInForm.get('password')!;
  // }

  onSubmit() {
     this.submitted = true
    if (this.signInForm.valid) {
       
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
  }

  signInWithGoogle() {
    const googleAuthUrl = `${environment.baseUrl}/auth/google`;

    window.open(
      googleAuthUrl,
      'GoogleAuth'
    );
  }

  togglePasswordVisibility() {
    console.log("hello")
    this.showPassword = !this.showPassword;
  }

  private handleMessage(event: MessageEvent) {
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
