@router.post("/platform/withdraw", status_code=status.HTTP_201_CREATED)
def withdraw_platform_commission(
    request: WithdrawRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Withdraw funds from platform wallet - Admin only.
    
    Allows admin to withdraw accumulated platform commission
    to a configured payment method.
    """
    # Only admins and super_admins can withdraw from platform wallet
    user_role_lower = current_user.role.lower()
    if user_role_lower not in [UserRole.ADMIN.value, UserRole.SUPER_ADMIN.value]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can withdraw platform commissions"
        )
    
    # Validate minimum withdrawal
    if request.amount <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Withdrawal amount must be greater than 0"
        )
    
    service = WalletService(db)
    
    # Platform wallet owner ID
    from uuid import UUID as UUID_TYPE
    platform_owner_id = UUID_TYPE('00000000-0000-0000-0000-000000000000')
    
    balance_info = service.get_balance(platform_owner_id, "platform")
    
    if balance_info["available_balance"] < request.amount:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Insufficient balance. Available: {balance_info['available_balance']} ETB"
        )
    
    try:
        from uuid import uuid4
        saga_id = str(uuid4())
        
        # Withdraw instantly (debit from available balance, not reserved)
        result = service.debit_wallet(
            owner_id=platform_owner_id,
            owner_type="platform",
            amount=Decimal(str(request.amount)),
            saga_id=saga_id,
            from_reserved=False,
            reference_type="platform_payout",
            reference_id=current_user.id
        )
        
        return {
            "message": "Platform commission withdrawn successfully",
            "transaction_id": result["transaction_id"],
            "amount": request.amount,
            "payment_method": request.payment_method,
            "new_balance": result["new_balance"],
            "status": "completed"
        }
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process platform withdrawal: {str(e)}"
        )
