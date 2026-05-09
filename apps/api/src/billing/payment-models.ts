/**
 * Kloud INDUSTRIAL PAYMENT MODELS
 * ===================================
 * Payment models for industrial use
 */

import { FastifyInstance } from "fastify";
import * as crypto from "crypto";

// =================================================================================
// ENUMS
// =================================================================================

export enum PaymentStatus {
  PENDING = "pending",
  COMPLETED = "completed",
  FAILED = "failed",
  REFUNDED = "refunded",
  PROCESSING = "processing"
}

export enum PaymentMethod {
  SEPA = "sepa",
  PAYPAL = "paypal"
}

// =================================================================================
// INTERFACES
// =================================================================================

export interface PaymentRecord {
  id: string;
  user_id: string;
  method: PaymentMethod;
  amount: number;
  currency: string;
  status: PaymentStatus;
  failure_reason: string | undefined;
  reference: string | undefined; // SEPA Ref / PayPal Txn ID
  refund_amount: number;
  created_at: string;
  updated_at: string;
  processed_at: string | undefined;
}

export interface PaymentConfig {
  SEPA_IBAN: string;
  SEPA_BIC: string;
  SEPA_HOLDER: string;
  PAYPAL_EMAIL: string;
  COMPANY: string;
}

export interface CreatePaymentRequest {
  user_id: string;
  amount: number;
  currency?: string;
  method: "sepa" | "paypal";
}

export interface ProcessPaymentRequest {
  payment_id: string;
  reference: string;
}

export interface RefundPaymentRequest {
  payment_id: string;
  amount: number;
  reason?: string;
}

// =================================================================================
// PAYMENT CONFIGURATION (REAL DATA)
// =================================================================================

export const PAYMENT_CONFIG: PaymentConfig = {
  SEPA_IBAN: process.env['SEPA_IBAN'] || "YOUR-IBAN-HERE",
  SEPA_BIC: process.env['SEPA_BIC'] || "YOUR-BIC-HERE",
  SEPA_HOLDER: process.env['SEPA_HOLDER'] || "Your Company Name",
  PAYPAL_EMAIL: process.env['PAYPAL_EMAIL'] || "payments@your-domain.com",
  COMPANY: "Kloud Cloud"
};

// =================================================================================
// IN-MEMORY STORAGE (Industrial grade simulation)
// =================================================================================

const payments = new Map<string, PaymentRecord>();

// =================================================================================
// PAYMENT CLASS
// =================================================================================

export class Payment {
  private data: PaymentRecord;

  constructor(data: Partial<PaymentRecord>) {
    this.data = {
      id: data.id || crypto.randomUUID(),
      user_id: data.user_id!,
      method: data.method!,
      amount: this.validateAmount(data.amount!),
      currency: data.currency || "EUR",
      status: data.status || PaymentStatus.PENDING,
      failure_reason: data.failure_reason,
      reference: data.reference,
      refund_amount: data.refund_amount || 0.0,
      created_at: data.created_at || new Date().toISOString(),
      updated_at: data.updated_at || new Date().toISOString(),
      processed_at: data.processed_at
    };
  }

  private validateAmount(amount: number): number {
    if (amount <= 0) {
      throw new Error("Payment amount must be positive");
    }
    return Math.round(amount * 100) / 100; // Round to 2 decimals
  }

  // =================================================================================
  // PROPERTIES
  // =================================================================================

  get id(): string {
    return this.data.id;
  }

  get formattedAmount(): string {
    return `${this.data.amount.toFixed(2)} ${this.data.currency}`;
  }

  get isSuccessful(): boolean {
    return this.data.status === PaymentStatus.COMPLETED;
  }

  get netAmount(): number {
    return this.data.amount - this.data.refund_amount;
  }

  get toJSON(): PaymentRecord {
    return { ...this.data };
  }

  // =================================================================================
  // ACTIONS
  // =================================================================================

  processPayment(reference: string): void {
    this.data.status = PaymentStatus.COMPLETED;
    this.data.reference = reference;
    this.data.processed_at = new Date().toISOString();
    this.data.updated_at = new Date().toISOString();
  }

  failPayment(reason: string): void {
    this.data.status = PaymentStatus.FAILED;
    this.data.failure_reason = reason;
    this.data.updated_at = new Date().toISOString();
  }

  refund(amount: number): void {
    if (amount <= 0 || amount > this.data.amount) {
      throw new Error("Invalid refund amount");
    }
    this.data.refund_amount = amount;
    this.data.status = PaymentStatus.REFUNDED;
    this.data.updated_at = new Date().toISOString();
  }

  setProcessing(): void {
    this.data.status = PaymentStatus.PROCESSING;
    this.data.updated_at = new Date().toISOString();
  }

  // =================================================================================
  // STORAGE METHODS
  // =================================================================================

  save(): Payment {
    payments.set(this.data.id, this.data);
    return this;
  }

  static findById(id: string): Payment | null {
    const data = payments.get(id);
    return data ? new Payment(data) : null;
  }

  static findByUserId(userId: string): Payment[] {
    const userPayments: Payment[] = [];
    for (const payment of payments.values()) {
      if (payment.user_id === userId) {
        userPayments.push(new Payment(payment));
      }
    }
    return userPayments.sort((a, b) => 
      new Date(b.toJSON.created_at).getTime() - new Date(a.toJSON.created_at).getTime()
    );
  }

  static getAll(): Payment[] {
    return Array.from(payments.values()).map(data => new Payment(data));
  }

  static getTotalRevenue(): number {
    let total = 0;
    for (const payment of payments.values()) {
      if (payment.status === PaymentStatus.COMPLETED) {
        total += payment.amount - payment.refund_amount;
      }
    }
    return Math.round(total * 100) / 100;
  }

  static getStats(): {
    total_payments: number;
    completed_payments: number;
    pending_payments: number;
    failed_payments: number;
    total_revenue: number;
    sepa_payments: number;
    paypal_payments: number;
  } {
    let completed = 0;
    let pending = 0;
    let failed = 0;
    let sepa = 0;
    let paypal = 0;
    
    for (const payment of payments.values()) {
      switch (payment.status) {
        case PaymentStatus.COMPLETED:
          completed++;
          break;
        case PaymentStatus.PENDING:
        case PaymentStatus.PROCESSING:
          pending++;
          break;
        case PaymentStatus.FAILED:
          failed++;
          break;
      }
      
      if (payment.method === PaymentMethod.SEPA) sepa++;
      if (payment.method === PaymentMethod.PAYPAL) paypal++;
    }

    return {
      total_payments: payments.size,
      completed_payments: completed,
      pending_payments: pending,
      failed_payments: failed,
      total_revenue: Payment.getTotalRevenue(),
      sepa_payments: sepa,
      paypal_payments: paypal
    };
  }
}

