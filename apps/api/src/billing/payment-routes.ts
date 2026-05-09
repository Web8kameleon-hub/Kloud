/**
 * Kloud INDUSTRIAL PAYMENT ROUTES
 * ===================================
 * REST API pÃ«r pagesa industriale me SEPA dhe PayPal
 * Real business data - Ledjan Ahmati / WEB8euroweb
 */

import { FastifyInstance, FastifyRequest, FastifyReply } from "fastify";
import { 
  Payment, 
  PaymentMethod, 
  PaymentStatus, 
  PAYMENT_CONFIG,
  CreatePaymentRequest,
  ProcessPaymentRequest,
  RefundPaymentRequest 
} from "./payment-models.js";

// =================================================================================
// REQUEST VALIDATION SCHEMAS
// =================================================================================

const createPaymentSchema = {
  body: {
    type: 'object',
    required: ['user_id', 'amount', 'method'],
    properties: {
      user_id: { type: 'string' },
      amount: { type: 'number', minimum: 0.01 },
      currency: { type: 'string', default: 'EUR' },
      method: { type: 'string', enum: ['sepa', 'paypal'] }
    }
  }
};

const processPaymentSchema = {
  body: {
    type: 'object',
    required: ['reference'],
    properties: {
      reference: { type: 'string', minLength: 1 }
    }
  },
  params: {
    type: 'object',
    required: ['payment_id'],
    properties: {
      payment_id: { type: 'string' }
    }
  }
};

const refundPaymentSchema = {
  body: {
    type: 'object',
    required: ['payment_id', 'amount'],
    properties: {
      payment_id: { type: 'string' },
      amount: { type: 'number', minimum: 0.01 },
      reason: { type: 'string' }
    }
  }
};

// =================================================================================
// PAYMENT ROUTES REGISTRATION
// =================================================================================

export async function registerPaymentRoutes(app: FastifyInstance) {

  // =================================================================================
  // CREATE PAYMENT - Krijo pagesÃ« tÃ« re
  // =================================================================================
  app.post("/billing/create", {
    schema: createPaymentSchema
  }, async (request: FastifyRequest, reply: FastifyReply) => {
    const body = request.body as CreatePaymentRequest;
    
    try {
      // Validate payment method
      const method = body.method === "sepa" ? PaymentMethod.SEPA : PaymentMethod.PAYPAL;
      
      // Create payment record
      const payment = new Payment({
        user_id: body.user_id,
        amount: body.amount,
        currency: body.currency || "EUR",
        method: method,
        status: PaymentStatus.PENDING
      }).save();

      // Return payment instructions based on method
      if (method === PaymentMethod.SEPA) {
        return {
          success: true,
          payment_id: payment.id,
          method: "SEPA Bank Transfer",
          instructions: {
            recipient_name: PAYMENT_CONFIG.SEPA_HOLDER,
            iban: PAYMENT_CONFIG.SEPA_IBAN,
            bic: PAYMENT_CONFIG.SEPA_BIC,
            amount: payment.formattedAmount,
            reference: `NEURO-${payment.id.substring(0, 8).toUpperCase()}`,
            company: PAYMENT_CONFIG.COMPANY,
            note: "Please include the reference number in your transfer"
          },
          status: payment.toJSON.status,
          created_at: payment.toJSON.created_at
        };
      }

      if (method === PaymentMethod.PAYPAL) {
        return {
          success: true,
          payment_id: payment.id,
          method: "PayPal",
          instructions: {
            paypal_email: PAYMENT_CONFIG.PAYPAL_EMAIL,
            recipient_name: PAYMENT_CONFIG.SEPA_HOLDER,
            amount: payment.formattedAmount,
            company: PAYMENT_CONFIG.COMPANY,
            reference: `NEURO-${payment.id.substring(0, 8).toUpperCase()}`,
            note: "Send payment to PayPal email with reference number"
          },
          status: payment.toJSON.status,
          created_at: payment.toJSON.created_at
        };
      }

      throw new Error("Invalid payment method");
      
    } catch (error: any) {
      reply.code(400);
      return {
        success: false,
        error: error.message || "Payment creation failed"
      };
    }
  });

  // =================================================================================
  // PROCESS PAYMENT - Konfirmo pagesÃ«n si tÃ« kryer
  // =================================================================================
  app.post("/billing/process/:payment_id", {
    schema: processPaymentSchema
  }, async (request: FastifyRequest, reply: FastifyReply) => {
    const { payment_id } = request.params as { payment_id: string };
    const { reference } = request.body as { reference: string };
    
    try {
      const payment = Payment.findById(payment_id);
      if (!payment) {
        reply.code(404);
        return {
          success: false,
          error: "Payment not found"
        };
      }

      // Check if already processed
      if (payment.toJSON.status === PaymentStatus.COMPLETED) {
        return {
          success: true,
          message: "Payment already completed",
          payment_id: payment.id,
          status: payment.toJSON.status,
          reference: payment.toJSON.reference
        };
      }

      // Mark as processing first
      payment.setProcessing();
      payment.save();

      // Simulate payment verification delay
      await new Promise(resolve => setTimeout(resolve, 1000));

      // Process the payment
      payment.processPayment(reference);
      payment.save();

      return {
        success: true,
        message: "Payment completed successfully",
        payment_id: payment.id,
        status: payment.toJSON.status,
        reference: payment.toJSON.reference,
        processed_at: payment.toJSON.processed_at,
        amount: payment.formattedAmount
      };

    } catch (error: any) {
      reply.code(400);
      return {
        success: false,
        error: error.message || "Payment processing failed"
      };
    }
  });

  // =================================================================================
  // REFUND PAYMENT - Kthe paratÃ«
  // =================================================================================
  app.post("/billing/refund", {
    schema: refundPaymentSchema
  }, async (request: FastifyRequest, reply: FastifyReply) => {
    const body = request.body as RefundPaymentRequest;
    
    try {
      const payment = Payment.findById(body.payment_id);
      if (!payment) {
        reply.code(404);
        return {
          success: false,
          error: "Payment not found"
        };
      }

      // Check if payment can be refunded
      if (payment.toJSON.status !== PaymentStatus.COMPLETED) {
        reply.code(400);
        return {
          success: false,
          error: "Only completed payments can be refunded"
        };
      }

      // Process refund
      payment.refund(body.amount);
      payment.save();

      return {
        success: true,
        message: "Refund processed successfully",
        payment_id: payment.id,
        refund_amount: `${body.amount.toFixed(2)} ${payment.toJSON.currency}`,
        net_amount: `${payment.netAmount.toFixed(2)} ${payment.toJSON.currency}`,
        status: payment.toJSON.status,
        reason: body.reason || "Refund requested"
      };

    } catch (error: any) {
      reply.code(400);
      return {
        success: false,
        error: error.message || "Refund processing failed"
      };
    }
  });

  // =================================================================================
  // GET PAYMENT STATUS - Kontrollo statusin e pagesÃ«s
  // =================================================================================
  app.get("/billing/payment/:payment_id", async (request: FastifyRequest, reply: FastifyReply) => {
    const { payment_id } = request.params as { payment_id: string };
    
    const payment = Payment.findById(payment_id);
    if (!payment) {
      reply.code(404);
      return {
        success: false,
        error: "Payment not found"
      };
    }

    return {
      success: true,
      payment: {
        id: payment.id,
        amount: payment.formattedAmount,
        method: payment.toJSON.method,
        status: payment.toJSON.status,
        reference: payment.toJSON.reference,
        created_at: payment.toJSON.created_at,
        processed_at: payment.toJSON.processed_at,
        refund_amount: payment.toJSON.refund_amount,
        net_amount: `${payment.netAmount.toFixed(2)} ${payment.toJSON.currency}`,
        is_successful: payment.isSuccessful
      }
    };
  });

  // =================================================================================
  // GET USER PAYMENTS - Merr tÃ« gjitha pagesat e njÃ« pÃ«rdoruesi
  // =================================================================================
  app.get("/billing/user/:user_id/payments", async (request: FastifyRequest, reply: FastifyReply) => {
    const { user_id } = request.params as { user_id: string };
    
    const payments = Payment.findByUserId(user_id);
    
    return {
      success: true,
      user_id: user_id,
      payments_count: payments.length,
      payments: payments.map(payment => ({
        id: payment.id,
        amount: payment.formattedAmount,
        method: payment.toJSON.method,
        status: payment.toJSON.status,
        reference: payment.toJSON.reference,
        created_at: payment.toJSON.created_at,
        processed_at: payment.toJSON.processed_at,
        net_amount: `${payment.netAmount.toFixed(2)} ${payment.toJSON.currency}`
      }))
    };
  });

  // =================================================================================
  // PAYMENT STATISTICS - Statistika pagesash
  // =================================================================================
  app.get("/billing/stats", async (request: FastifyRequest, reply: FastifyReply) => {
    const stats = Payment.getStats();
    
    return {
      success: true,
      business_owner: PAYMENT_CONFIG.SEPA_HOLDER,
      company: PAYMENT_CONFIG.COMPANY,
      statistics: {
        total_payments: stats.total_payments,
        completed_payments: stats.completed_payments,
        pending_payments: stats.pending_payments,
        failed_payments: stats.failed_payments,
        total_revenue: `${stats.total_revenue.toFixed(2)} EUR`,
        payment_methods: {
          sepa_transfers: stats.sepa_payments,
          paypal_payments: stats.paypal_payments
        },
        success_rate: stats.total_payments > 0 
          ? `${(stats.completed_payments / stats.total_payments * 100).toFixed(1)}%` 
          : "0%"
      },
      payment_config: {
        sepa_iban: PAYMENT_CONFIG.SEPA_IBAN,
        paypal_email: PAYMENT_CONFIG.PAYPAL_EMAIL,
        supported_currencies: ["EUR"],
        minimum_amount: "0.01 EUR"
      },
      timestamp: new Date().toISOString()
    };
  });

  // =================================================================================
  // PAYMENT CONFIG INFO - Informacione konfigurimi
  // =================================================================================
  app.get("/billing/config", async (request: FastifyRequest, reply: FastifyReply) => {
    return {
      success: true,
      payment_methods: {
        sepa: {
          name: "SEPA Bank Transfer",
          recipient: PAYMENT_CONFIG.SEPA_HOLDER,
          iban: PAYMENT_CONFIG.SEPA_IBAN,
          bic: PAYMENT_CONFIG.SEPA_BIC,
          company: PAYMENT_CONFIG.COMPANY,
          processing_time: "1-3 business days",
          fees: "No additional fees"
        },
        paypal: {
          name: "PayPal",
          email: PAYMENT_CONFIG.PAYPAL_EMAIL,
          recipient: PAYMENT_CONFIG.SEPA_HOLDER,
          company: PAYMENT_CONFIG.COMPANY,
          processing_time: "Instant",
          fees: "PayPal standard fees apply"
        }
      },
      supported_currencies: ["EUR"],
      minimum_amount: 0.01,
      company_info: {
        name: PAYMENT_CONFIG.COMPANY,
        owner: PAYMENT_CONFIG.SEPA_HOLDER,
        location: "Germany"
      }
    };
  });

  // =================================================================================
  // FAIL PAYMENT - Vendor pagesÃ«n si tÃ« dÃ«shtuar (manual)
  // =================================================================================
  app.post("/billing/fail/:payment_id", async (request: FastifyRequest, reply: FastifyReply) => {
    const { payment_id } = request.params as { payment_id: string };
    const { reason } = request.body as { reason?: string };
    
    try {
      const payment = Payment.findById(payment_id);
      if (!payment) {
        reply.code(404);
        return {
          success: false,
          error: "Payment not found"
        };
      }

      payment.failPayment(reason || "Payment failed - reason not specified");
      payment.save();

      return {
        success: true,
        message: "Payment marked as failed",
        payment_id: payment.id,
        status: payment.toJSON.status,
        failure_reason: payment.toJSON.failure_reason
      };

    } catch (error: any) {
      reply.code(400);
      return {
        success: false,
        error: error.message || "Failed to mark payment as failed"
      };
    }
  });
}

